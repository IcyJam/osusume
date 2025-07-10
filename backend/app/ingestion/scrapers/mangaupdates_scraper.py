import asyncio
import json
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Sequence

import httpx
from tqdm import tqdm

# Obtained from their API at https://api.mangaupdates.com/v1/genres on 2025.07.09
GENRES = ['Action', 'Adult', 'Adventure', 'Comedy', 'Doujinshi', 'Drama', 'Ecchi', 'Fantasy', 'Gender Bender', 'Harem',
          'Hentai', 'Historical', 'Horror', 'Josei', 'Lolicon', 'Martial Arts', 'Mature', 'Mecha', 'Mystery',
          'Psychological', 'Romance', 'School Life', 'Sci-fi', 'Seinen', 'Shotacon', 'Shoujo', 'Shoujo Ai', 'Shounen',
          'Shounen Ai', 'Slice of Life', 'Smut', 'Sports', 'Supernatural', 'Tragedy', 'Yaoi', 'Yuri']

MANGAUPDATES_API_BASE_URL = "https://api.mangaupdates.com/v1"
SERIES_URL = MANGAUPDATES_API_BASE_URL + "/series"
SEARCH_URL = SERIES_URL + "/search"
DEFAULT_ID_STORE_PATH = Path("/data/mangaupdates/ids")
DEFAULT_ID_STORE_FILE_NAME = "series_ids.jsonl"
DEFAULT_ID_STORE_FILE_PATH = Path("/data/mangaupdates/ids/series_ids.jsonl")
DEFAULT_SERIES_STORE_ROOT = Path("/data/mangaupdates/series")


def get_all_manga_ids(start_year_1=1900,
                      end_year_1=2014,
                      start_year_2=2015,
                      end_year_2=None,
                      delay=1.0,
                      id_store_path: str | Path = DEFAULT_ID_STORE_PATH,
                      id_store_file_name: str = DEFAULT_ID_STORE_FILE_NAME,
                      ):
    """
    Retrieves all series IDs from the MangaUpdates API, using the search endpoint.
    :param start_year_1: The year 1 range should only contain years when there are less than 10,000 series.
    :param end_year_1: The year 1 range should only contain years when there are less than 10,000 series.
    :param start_year_2: Search on year 2 range will be split by genre (36 of them), but is suitable for years with more than 10,000 series.
    :param end_year_2: Search on year 2 range will be split by genre (36 of them), but is suitable for years with more than 10,000 series.
    :param delay: Delay between each request (in seconds).
    :param id_store_path: Default directory to store the JSONL file containing all IDs.
    :param id_store_file_name: Default path to store the JSONL file containing all IDs.
    """
    if end_year_2 is None:
        end_year_2 = datetime.today().year

    # Convert paths
    if isinstance(id_store_path, str): id_store_path = Path(id_store_path)
    id_store_file_path = id_store_path / id_store_file_name

    # Make directory if it does not exist
    id_store_path.mkdir(parents=True, exist_ok=True)
    seen_ids = set()

    # Load already saved IDs
    if id_store_file_path.exists():
        with id_store_file_path.open("r", encoding="utf-8") as f:
            for line in f:
                seen_ids.add(json.loads(line)["series_id"])

    def save_id(_record):
        """ Writes a series ID from a record at the end of the ID store file."""
        with id_store_file_path.open("a", encoding="utf-8") as _f:  # "a" for "append"
            _f.write(json.dumps({"series_id": _record["series_id"]}) + "\n")

    def get_search_results(_payload):
        _headers = {
            "Authorization": "bearerAuth",
            "Content-Type": "application/json"
        }
        response = http_request_with_backoff(
            method="POST",
            url=SEARCH_URL,
            headers=_headers,
            json_payload=_payload,
            timeout=30,
            max_retries=5,
            delay=delay
        )
        if response is not None:
            return response.json()
        return None

    def iterate_payloads():
        """Yield search‑payload dictionaries, minimizing hit counts."""

        # Years with <10 000 hits – no genre slicing needed
        for year in range(start_year_1, end_year_1 + 1):
            yield {"year": year}

        # Years with potentially >10 000 hits – slice by genre,
        # always excluding every genre we have already queried
        for year in range(start_year_2, end_year_2 + 1):
            seen_genres: list[str] = []  # genres already used for this year
            for genre in GENRES:
                yield {
                    "year": year,
                    "genre": [genre],
                    "exclude_genre": seen_genres  # progressively larger exclusion list
                }
                seen_genres.append(genre)  # add current genre to exclusions

            # Final catch‑all query (no genre), excluding all 36 genres
            yield {"year": year, "exclude_genre": GENRES}

    for payload in iterate_payloads():
        found = 0
        page = 1
        while True:
            payload["page"] = page
            print(f"Fetching page {page} for payload: {payload}")
            result = get_search_results(payload)
            if not result or "results" not in result:
                break
            elif not result["results"]:
                break

            for item in result["results"]:
                record = item.get("record")
                if not record:
                    continue
                series_id = record["series_id"]
                if series_id not in seen_ids:
                    save_id(record)
                    seen_ids.add(series_id)
                    found += 1

            page += 1
            time.sleep(delay)  # respectful delay
        print(f"Saved {found} series IDs")

        time.sleep(delay)  # delay between different search payloads

    print(f"ID Scraping complete. Total unique IDs collected: {len(seen_ids)}")


def _shard_dir(series_id: str | int) -> str:
    """Return a 3‑digit shard directory based on the first 3 digits of the ID."""
    return str(series_id).zfill(3)[:3]


async def _fetch_and_store(
        series_id: str,
        series_store_root: Path,
        headers: dict,
        delay: float,
        sem: asyncio.Semaphore,
):
    """Single asynchronous fetch wrapped in a semaphore."""
    async with sem: # sem is the maximum number of concurrent requests
        shard = _shard_dir(series_id)
        series_path = series_store_root / shard
        series_path.mkdir(parents=True, exist_ok=True)
        file_path = series_path / f"{series_id}.json"

        if file_path.exists():
            return "skipped"

        # Run the (sync) http_request_with_backoff in a thread to avoid blocking event loop
        response = await asyncio.to_thread(
            http_request_with_backoff,
            method="GET",
            url=f"{SERIES_URL}/{series_id}",
            headers=headers,
            delay=delay,
        )

        if response is None:
            return "failed"

        with open(file_path, "w", encoding="utf-8") as fp:
            fp.write(response.text)

        # Pause between this worker’s requests
        await asyncio.sleep(delay + random.uniform(0,0.3))
        return "downloaded"


async def _run_all_tasks(
        ids: Sequence[str],
        series_store_root: Path,
        delay: float,
        max_in_flight: int,
):
    headers = {
        "Authorization": "bearerAuth",
        "Content-Type": "application/json",
    }
    sem = asyncio.Semaphore(max_in_flight)

    tasks = [
        _fetch_and_store(series_id, series_store_root, headers, delay, sem)
        for series_id in ids
    ]

    downloaded = skipped = failed = 0
    for future in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Downloading series", unit="series"):
        status = await future
        if status == "downloaded":
            downloaded += 1
        elif status == "skipped":
            skipped += 1
        else:
            failed += 1

    return downloaded, skipped, failed, len(tasks)


def get_all_series(
        id_store_file_path: str | Path,
        series_store_root: str | Path = DEFAULT_SERIES_STORE_ROOT,
        delay: float = 0.5,
        max_in_flight: int = 2,
):
    """
    Download every series in `id_store_file_path` using up to `max_in_flight`
    simultaneous requests.

    :param id_store_file_path: Path to series_ids.jsonl containing all series IDs to download.
    :param series_store_root : Root folder in which to store JSON files.
    :param delay: Base delay (seconds) per worker.
    :param max_in_flight: Number of HTTP requests allowed in flight at once.
    """
    series_store_root = Path(series_store_root)
    series_store_root.mkdir(parents=True, exist_ok=True)

    # Load all IDs
    with open(id_store_file_path, "r", encoding="utf-8") as f:
        ids = [json.loads(line)["series_id"] for line in f if line.strip()]

    downloaded, skipped, failed, total = asyncio.run(
        _run_all_tasks(ids, series_store_root, delay, max_in_flight)
    )

    print(
        f"\nFinished. Downloaded {downloaded}, skipped {skipped}, "
        f"failed {failed}, total IDs {total}."
    )


def http_request_with_backoff(
        method: str,
        url: str,
        headers: dict = None,
        json_payload: dict = None,
        params: dict = None,
        timeout: float = 30,
        max_retries: int = 5,
        delay: float = 1.0
):
    """
    Sends an HTTP request with retries and exponential backoff on transient errors.

    :param method: HTTP method like 'GET', 'POST', etc.
    :param url: Full URL of the request.
    :param headers: Optional headers dictionary.
    :param json_payload: Optional JSON payload (for POST, PUT).
    :param params: Optional URL query parameters (for GET).
    :param timeout: Timeout in seconds for the request.
    :param max_retries: Number of retries on failure.
    :param delay: Base delay in seconds for backoff.
    :return: Httpx.Response object on success, None on failure.
    """
    method = method.upper()
    for attempt in range(max_retries):
        try:
            with httpx.Client() as client:
                response = client.request(
                    method,
                    url,
                    headers=headers,
                    json=json_payload,
                    params=params,
                    timeout=timeout
                )
            if response.status_code == 200:
                return response
            elif response.status_code in {429, 500, 502, 503, 504}:
                sleep_time = delay * (2 ** attempt)
                tqdm.write(f"Retry {attempt + 1}/{max_retries} after {sleep_time}s due to status {response.status_code}")
                time.sleep(sleep_time)
            else:
                tqdm.write(f"HTTP error {response.status_code}: {response.text}")
                return None
        except Exception as e:
            sleep_time = delay * (2 ** attempt)
            tqdm.write(f"Exception on attempt {attempt + 1}/{max_retries}: {e}. Retrying in {sleep_time}s")
            time.sleep(sleep_time)
    return None
