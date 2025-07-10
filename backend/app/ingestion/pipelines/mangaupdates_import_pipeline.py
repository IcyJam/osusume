from app.ingestion.scrapers.mangaupdates_scraper import DEFAULT_ID_STORE_PATH, DEFAULT_ID_STORE_FILE_NAME, \
    get_all_manga_ids


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
