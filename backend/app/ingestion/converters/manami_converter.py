from datetime import date
from urllib.parse import urlparse


def convert_media_entry(entry: dict) -> dict:
    return {
        "type": convert_type(entry.get("type")),
        "title": entry.get("title"),
        "summary": None,  # the anime offline database does not include summaries
        "start_date": convert_date(entry.get("animeSeason", None)),
        "end_date": None,
        "external_url": convert_external_url(entry.get("sources")),
        "image_url": entry.get("picture"),
        "status": convert_status(entry.get("status")),
        "score": convert_score(entry.get("score")),
        "content_descriptors": entry.get("tags"),
    }


def convert_date(anime_season: dict | None) -> date | None:
    if anime_season is None:
        return None

    season_name: str | None = anime_season.get("season", None)
    year: int | None = anime_season.get("year", None)

    if year is None:  # if no year is provided, we can't make a date from the season anyway
        return None

    else:
        # give an approximate date depending on the season
        season_month = 1
        if season_name == "SPRING": season_month = 4
        if season_name == "SUMMER": season_month = 7
        if season_name == "FALL": season_month = 10
        if season_name == "WINTER": season_month = 1

        return date(year=year, month=season_month, day=1)


def convert_type(entry_type: str) -> str:
    if entry_type == "TV":
        return "TV"
    if entry_type == "MOVIE":
        return "MOVIE"
    if entry_type == "OVA":
        return "OVA"
    if entry_type == "ONA":
        return "ONA"
    if entry_type == "SPECIAL":
        return "SPECIAL"
    else:
        return "OTHER"


def convert_status(status: str) -> str | None:
    if status == "FINISHED":
        return "FINISHED"
    elif status == "ONGOING":
        return "ONGOING"
    elif status == "UPCOMING":
        return "UPCOMING"
    elif status == "UNKNOWN":
        return "UNKNOWN"
    else:
        return None


def convert_external_url(urls: list[str]) -> str | None:
    if not urls:
        return None

    priority = [
        "anilist.co",
        "myanimelist.net",
        "livechart.me",
        "anidb.net",
    ]

    # Map exact domains to URLs
    domain_to_url = {}
    for url in urls:
        try:
            domain = urlparse(url).netloc.lower()
            domain_to_url[domain] = url
        except Exception:  # Ignore malformed URLs
            continue

    # Check if any preferred domain is present
    for preferred in priority:
        if preferred in domain_to_url:
            return domain_to_url[preferred]

    # Fallback to first URL
    return urls[0]


def convert_score(score: dict) -> float | None:
    if score is not None:
        return score.get("median")
    else:
        return None
