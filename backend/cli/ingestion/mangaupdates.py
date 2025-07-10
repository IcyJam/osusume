import typer

from app.ingestion.scrapers.mangaupdates_scraper import DEFAULT_ID_STORE_PATH, DEFAULT_ID_STORE_FILE_NAME, \
    get_all_manga_ids
import typer

from app.ingestion.scrapers.mangaupdates_scraper import DEFAULT_ID_STORE_PATH, DEFAULT_ID_STORE_FILE_NAME, \
    get_all_manga_ids

app = typer.Typer()


@app.command()
def get_series_ids(
        start_year_1: int = typer.Option(
            default=1900,
            help="Start year for a range of years that all have under 10,000 series."),
        end_year_1: int = typer.Option(
            default=2014,
            help="End year for a range of years that all have under 10,000 series."),
        start_year_2: int = typer.Option(
            default=2015,
            help="Start year for a range of years that may have over 10,000 series."),
        end_year_2: int = typer.Option(
            default=None,
            help="End year for a range of years that may have over 10,000 series."),
        delay: float = typer.Option(
            default=1.0,
            help="Delay between each request (in seconds)."),
        id_store_path: str = typer.Option(
            default=DEFAULT_ID_STORE_PATH,
            help="Path of the directory to store the series ids."),
        id_store_file_name: str = typer.Option(
            default=DEFAULT_ID_STORE_FILE_NAME,
            help="Name of the file to store the series ids."),
):
    """ Download all manga IDs from MangaUpdates and store them to a JSONL file. """
    get_all_manga_ids(
        start_year_1=start_year_1,
        end_year_1=end_year_1,
        start_year_2=start_year_2,
        end_year_2=end_year_2,
        delay=delay,
        id_store_path=id_store_path,
        id_store_file_name=id_store_file_name,
    )
