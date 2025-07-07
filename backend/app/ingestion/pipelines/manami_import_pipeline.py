import json
import os

from app.db.database import SessionLocal
from app.ingestion.converters.manami_converter import convert_media_entry
from app.ingestion.loaders.media_loader import load_all_media
from app.ingestion.scrapers.manami_scraper import download_database, ANIME_DATABASE_ASSET_NAME
from tqdm import tqdm


def import_manami_from_repo():
    print("Importing media entries from Manami project database.")
    try:
        download_database(local_save_dir="")
        print("✅ Download successful.")
    except Exception as e:
        print("❌ Failed to download:", e)
        return

    try:
        load_file_into_database(ANIME_DATABASE_ASSET_NAME)

    except Exception as e:
        print("An error occurred during import:", e)

    finally:
        print("Removing local file...")
        os.remove(ANIME_DATABASE_ASSET_NAME)


def import_manami_from_file(filepath: str):
    print(f"Importing media entries from local file: {filepath}")

    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return

    try:
        load_file_into_database(filepath)

    except Exception as e:
        print("An error occurred during import:", e)


def load_file_into_database(path: str):
    print("Converting media entries...")
    with open(path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    entries = raw_data["data"]
    transformed = [convert_media_entry(entry) for entry in tqdm(entries, desc="Converting media entries")]

    print("Loading into database...")
    with SessionLocal() as session:
        load_all_media(session, transformed)
    print("Media entries successfully imported into the database!")
