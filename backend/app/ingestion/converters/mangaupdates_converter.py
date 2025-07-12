from datetime import date


def convert_media_entry(entry: dict) -> dict:
    return {
        "type"                  : convert_type(entry.get("type")),
        "title"                 : entry.get("title"),
        "summary"               : entry.get("description"),
        "start_date"            : convert_date(entry.get("year")),
        "end_date"              : None,
        "external_url"          : entry.get("url"),
        "image_url"             : convert_image(entry.get("image")),
        "status"                : convert_status(entry.get("completed"),entry.get("status")),
        "score"                 : entry.get("bayesian_rating"),
        "content_descriptors"   : convert_content_descriptors(entry.get("genres"), entry.get("categories")),
    }


def convert_type(entry_type: str) -> str:
    if entry_type == "Artbook":
        return "ARTBOOK"
    if entry_type == "Doujinshi":
        return "DOUJINSHI"
    if entry_type == "Manga":
        return "MANGA"
    if entry_type == "Novel":
        return "NOVEL"
    if entry_type == "Manhwa":
        return "MANHWA"
    if entry_type == "Manhua":
        return "MANHWA"
    else:
        return "OTHER"


def convert_date(year_string: str) -> date | None:
    try:
        return date(year=int(year_string), month=1, day=1)
    except Exception:
        return None


def convert_image(image_dict: dict) -> str | None:
    try:
        return image_dict.get("url").get("original")

    except Exception:
        return None


def convert_status(completed_bool: bool, status: str) -> str | None:
    if completed_bool:
        return "FINISHED"
    elif status is None:
        return None
    elif "Complete" in status:
        return "FINISHED"
    elif "Ongoing" in status:
        return "ONGOING"
    elif "Hiatus" in status:
        return "SUSPENDED"
    elif status == "Cancelled":
        return "CANCELLED"
    else:
        return None


def convert_content_descriptors(genres: list, categories: list) -> list[str] | None:
    content_descriptors = []
    for genre in genres:
        if genre.get("genre"): content_descriptors.append(genre["genre"])
    for category in categories:
        if category.get("category"): content_descriptors.append(category["category"])

    return content_descriptors
