import json
import os

from tqdm import tqdm

from db.database import SessionLocal
from ingestion.converters.manami_converter import convert_media_entry
from ingestion.loaders.media_loader import load_all_media
from ingestion.scrapers.manami_scraper import download_database, ANIME_DATABASE_ASSET_NAME


def run_import():
    print("Importing media entries from Manami project database.")
    try:
        download_database(local_save_dir="")
        print("✅ Download successful.")
    except Exception as e:
        print("❌ Failed to download:", e)
        return

    try:
        print("Converting media entries...")
        with open(ANIME_DATABASE_ASSET_NAME, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        entries = raw_data["data"]
        transformed = [convert_media_entry(entry) for entry in tqdm(entries, desc="Converting media entries")]

        print("Loading into database...")
        with SessionLocal() as session:
            load_all_media(session, transformed)

        print("Media successfully imported.")
        print("Media entries successfully imported into the database!")

    finally:
        print("Removing local file...")
        os.remove(ANIME_DATABASE_ASSET_NAME)


if __name__ == "__main__":
    run_import()
