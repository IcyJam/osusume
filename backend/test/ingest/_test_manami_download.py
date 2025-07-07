import os

import ingestion.scrapers.manami_scraper as manami_scraper


def test_manami_download():
    try:
        manami_scraper.download_database(local_save_dir="")
        print("✅ Download successful.")
        os.remove(manami_scraper.ANIME_DATABASE_ASSET_NAME)
        print("Downloaded file removed.")
    except Exception as e:
        print("❌ Failed to download:", e)


if __name__ == "__main__":
    test_manami_download()
