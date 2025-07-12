import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Union

from tqdm import tqdm

from app.db.database import SessionLocal
from app.ingestion.converters.mangaupdates_converter import convert_media_entry
from app.ingestion.loaders.media_loader import load_all_media
from app.ingestion.scrapers.mangaupdates_scraper import DEFAULT_ID_STORE_PATH, DEFAULT_ID_STORE_FILE_NAME, \
    get_all_manga_ids, DEFAULT_SERIES_STORE_ROOT, DEFAULT_ID_STORE_FILE_PATH, get_all_series

DEFAULT_MANGAUPDATES_JSON_STORE_ROOT = Path("/data/mangaupdates/")


def download_mangaupdates_series_ids(
        start_year_1=1900,
        end_year_1=2014,
        start_year_2=2015,
        end_year_2=None,
        delay=1.0,
        id_store_path=DEFAULT_ID_STORE_PATH,
        id_store_file_name=DEFAULT_ID_STORE_FILE_NAME,
):
    try:
        get_all_manga_ids(
            start_year_1=start_year_1,
            end_year_1=end_year_1,
            start_year_2=start_year_2,
            end_year_2=end_year_2,
            delay=delay,
            id_store_path=id_store_path,
            id_store_file_name=id_store_file_name,
        )
    except Exception as e:
        print("An error occurred during import:", e)


def download_mangaupdates_series(
        id_store_file_path=DEFAULT_ID_STORE_FILE_PATH,
        series_store_root=DEFAULT_SERIES_STORE_ROOT,
        delay: float = 0.5,
        max_in_flight=2,
):
    try:
        get_all_series(
            id_store_file_path=id_store_file_path,
            series_store_root=series_store_root,
            delay=delay,
            max_in_flight=max_in_flight
        )
    except Exception as e:
        print("An error occurred during import:", e)


def _read_json(path: Path):
    """ Helper for threaded reads."""
    try:
        with path.open("r", encoding="utf-8") as fp:
            return json.load(fp)
    except Exception as e:
        return {"__error__": str(e), "__path__": str(path)}


def merge_mangaupdates_json(
        series_store_root=DEFAULT_SERIES_STORE_ROOT,
        output_dir=DEFAULT_SERIES_STORE_ROOT,
        batch_size: int = 1_000,
        max_workers: int = 8
):
    """
    Merge every per‑series JSON file in `series_store_root` into a single JSONL
    file (`mangaupdates_series.jsonl`) in `output_dir`.

    :param series_store_root: Root directory of series.
    :param output_dir: Output directory for merged JSONL file.
    :param batch_size: Number of files to merge in one batch.
    :param max_workers: Maximum number of threads to use for I/O operations.

    """
    series_store_root = Path(series_store_root)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "mangaupdates_series.jsonl"

    json_files = list(series_store_root.rglob("*.json"))
    total_files = len(json_files)
    if total_files == 0:
        print("No JSON files found; nothing to merge.")
        return

    # Load existing IDs if output already exists
    existing_ids = set()
    if out_path.exists():
        with out_path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    existing_ids.add(json.loads(line)["series_id"])
                except Exception:
                    pass  # ignore corrupt line

    written = skipped = 0
    buffer = []

    with out_path.open("a", encoding="utf-8", buffering=1_048_576) as outfile:  # 1MB buffer
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = [pool.submit(_read_json, p) for p in json_files]

            for future in tqdm(as_completed(futures), total=total_files, desc="Merging series", unit="file"):
                data = future.result()
                # If read failed, ignore
                if "__error__" in data:  # read failed
                    tqdm.write(f"Failed {data['__path__']}: {data['__error__']}")
                    continue

                series_id = data.get("series_id")
                # If the series exists, skip
                if series_id in existing_ids:
                    skipped += 1
                    continue

                # Otherwise, add the series to a buffer. The batch contained in the buffer will be written all at once.
                buffer.append(json.dumps(data, separators=(",", ":")))
                existing_ids.add(series_id)
                written += 1

                # Flush batch
                if len(buffer) >= batch_size:
                    outfile.write("\n".join(buffer) + "\n")
                    buffer.clear()

        # Final flush
        if buffer:
            outfile.write("\n".join(buffer) + "\n")

    print(f"Finished. Added {written} new series. Skipped {skipped} duplicates. "
          f"Total lines in output: {len(existing_ids)}.")


def import_mangaupdates_from_file(filepath: str, max_workers: int = 8, batch_size: int = 5000):
    print(f"Importing media entries from local file: {filepath}")

    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return

    load_file_into_database(filepath, max_workers, batch_size)


def load_file_into_database(
        filepath: Union[str, Path],
        max_workers: int = 8,
        batch_size: int | None = 5_000,
) -> None:
    """
    Stream a .jsonl dump, convert each record, and bulk‑insert the results into the database.

    :param filepath: Path to the ``.jsonl`` file produced by the merge step. Each line must contain one complete JSON object with the original MangaUpdates schema.
    :param max_workers: Number of worker threads used for parallel conversion.
    :param batch_size: Number of converted entries inserted in one DB batch.
    """

    filepath = Path(filepath)

    # Count lines for tqdm
    print("Counting lines…")
    with filepath.open("r", encoding="utf-8") as fp:
        total_lines = sum(1 for _ in fp)

    # Convert entries in parallel with thread pool
    print("Converting media entries…")
    transformed: List[dict] = []

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        with filepath.open("r", encoding="utf-8") as fp:
            futures = [
                pool.submit(convert_media_entry, json.loads(line))
                for line in tqdm(
                    fp,
                    total=total_lines,
                    desc="Creating_tasks",
                    unit="entry",
                )
            ]

            for future in tqdm(
                    as_completed(futures),
                    total=total_lines,
                    desc="Converting media entries",
                    unit="entry",
            ):
                transformed.append(future.result())

    # Bulk insert into the database
    print("Loading into database…")
    with SessionLocal() as session:
        for start in tqdm(
                range(0, len(transformed), batch_size),
                desc="Inserting into database",
                unit="batch",
                position=0
        ):
            load_all_media(session, transformed[start:start + batch_size])

    print("Media entries successfully imported into the database!")
