import typer

from app.ingestion.pipelines.mangaupdates_import_pipeline import download_mangaupdates_series_ids, \
    download_mangaupdates_series, merge_mangaupdates_json, DEFAULT_MANGAUPDATES_JSON_STORE_ROOT, \
    import_mangaupdates_from_file
from app.ingestion.scrapers.mangaupdates_scraper import DEFAULT_ID_STORE_FILE_PATH, DEFAULT_SERIES_STORE_ROOT
from app.ingestion.scrapers.mangaupdates_scraper import DEFAULT_ID_STORE_PATH, DEFAULT_ID_STORE_FILE_NAME

app = typer.Typer()


@app.command()
def download_series_ids(
        start_year_1: int = typer.Option(
            default=1900,
            help="Start year for a range of years that all have under 10,000 series."
        ),
        end_year_1: int = typer.Option(
            default=2014,
            help="End year for a range of years that all have under 10,000 series."
        ),
        start_year_2: int = typer.Option(
            default=2015,
            help="Start year for a range of years that may have over 10,000 series."
        ),
        end_year_2: int = typer.Option(
            default=None,
            help="End year for a range of years that may have over 10,000 series."
        ),
        delay: float = typer.Option(
            default=1.0,
            help="Delay between each request (in seconds)."
        ),
        id_store_path: str = typer.Option(
            default=DEFAULT_ID_STORE_PATH,
            help="Path of the directory to store the series IDs."
        ),
        id_store_file_name: str = typer.Option(
            default=DEFAULT_ID_STORE_FILE_NAME,
            help="Name of the file to store the series IDs."
        ),
):
    """ Download all series IDs from MangaUpdates and store them to a JSONL file. """
    download_mangaupdates_series_ids(
        start_year_1=start_year_1,
        end_year_1=end_year_1,
        start_year_2=start_year_2,
        end_year_2=end_year_2,
        delay=delay,
        id_store_path=id_store_path,
        id_store_file_name=id_store_file_name,
    )


@app.command()
def download_all_series(
        id_store_file_path: str = typer.Option(
            default=DEFAULT_ID_STORE_FILE_PATH,
            help="Name of the file where series IDs are stored."
        ),
        series_store_root=typer.Option(
            default=DEFAULT_SERIES_STORE_ROOT,
            help="Name of the root directory where series JSONs will be stored."
        ),
        delay: float = typer.Option(
            default=0.5,
            help="Delay between each request (in seconds)."
        ),
        max_in_flight: int = typer.Option(
            default=2,
            help="Maximum number of concurrent workers."
        )
):
    """ Download all series objects from MangaUpdates and store them to JSON files in the given directory. """
    download_mangaupdates_series(
        id_store_file_path=id_store_file_path,
        series_store_root=series_store_root,
        delay=delay,
        max_in_flight=max_in_flight
    )


@app.command()
def merge_mangaupdates_series(
        series_store_root: str = typer.Option(
            default=DEFAULT_SERIES_STORE_ROOT,
            help="Path of the directory where series JSONs are stored."
        ),
        output_dir=typer.Option(
            default=DEFAULT_MANGAUPDATES_JSON_STORE_ROOT,
            help="Path of the directory where the merged JSON will be stored."
        ),
        batch_size: int = typer.Option(
            default=1_000,
            help="Number of series to merge at once."
        ),
        max_workers: int = typer.Option(
            default=8,
            help="Maximum number of concurrent workers."
        ),
):
    """ Merge downloaded JSONs and output a merged JSONL file at the output directory. """
    merge_mangaupdates_json(
        series_store_root=series_store_root,
        output_dir=output_dir,
        batch_size=batch_size,
        max_workers=max_workers,
    )


@app.command()
def from_file(
        path: str = typer.Argument(..., help="JSONL file path"),
        max_workers: int = typer.Option(
            default=8,
            help="Maximum number of concurrent workers for parallel conversion."
        ),
        batch_size: int = typer.Option(
            default=5_000,
            help="Number of converted entries inserted in one database batch."
        ),
):
    """Ingest Mangaupdates from a local file."""
    import_mangaupdates_from_file(path, max_workers=max_workers, batch_size=batch_size)
