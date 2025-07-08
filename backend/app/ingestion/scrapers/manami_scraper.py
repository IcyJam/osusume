import os

import httpx
from tqdm import tqdm

from common.env import get_env_variable

PROJECT_URL = "https://api.github.com/repos/manami-project/anime-offline-database"
ANIME_DATABASE_ASSET_NAME = "anime-offline-database.json"


def download_with_progress(download_url: str, headers: dict, output_path: str):
    with httpx.Client(follow_redirects=True) as client:
        with client.stream("GET", download_url, headers=headers) as response:
            if response.status_code != 200:
                print("Failed to download:", response.status_code)
                return

            total = int(response.headers.get("Content-Length", 0))
            chunk_size = 8192

            with open(output_path, "wb") as file, tqdm(
                    total=total, unit="B", unit_scale=True, desc="Downloading"
            ) as progress:
                for chunk in response.iter_bytes(chunk_size=chunk_size):
                    file.write(chunk)
                    progress.update(len(chunk))

    print(f"Download complete. File saved to {output_path}")


def download_database(local_save_dir):
    """
    Downloads the anime offline database from its latest GitHub release. It is expected to be a JSON file.
    :param local_save_dir: Directory to save the database file to.
    """
    github_token = get_env_variable("GITHUB_TOKEN")

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "anime-recommender",
        "Authorization": f"Bearer {github_token}"
    }

    with httpx.Client() as client:
        # 1. Get all releases
        releases_url = f"{PROJECT_URL}/releases"
        print(f"Fetching releases from {releases_url}...")
        release_response = client.get(releases_url, headers=headers, follow_redirects=True)
        releases = release_response.json()

        # 2. Pick the latest release with assets
        release = next((r for r in releases if not r["draft"] and r["assets"]), None)
        if not release:
            print("No release with assets found.")
            return

        # 3. Pick the database file
        asset = next((a for a in release["assets"] if a["name"] == ANIME_DATABASE_ASSET_NAME), None)
        if not asset:
            print("No asset found.")
            return
        asset_api_url = asset["url"]

        # 4. Download asset via API URL
        print(f"Downloading anime database at {asset_api_url}.")

        download_with_progress(
            asset_api_url,
            headers={
                "Accept": "application/octet-stream",
                "User-Agent": "anime-recommender",
                "Authorization": f"Bearer {github_token}",
            },
            output_path=os.path.join(local_save_dir, ANIME_DATABASE_ASSET_NAME),
        )
