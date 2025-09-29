from typing import Optional

from pydantic import BaseModel

from app.db.models import Media


class MediaResponse(BaseModel):
    title: str
    type: str
    url: Optional[str]
    status: Optional[str]
    score: Optional[float]


def convert_media(media: Media) -> MediaResponse:
    return MediaResponse(
        title=media.title,
        type=media.type,
        url=media.external_url,
        status=media.status,
        score=float(round(media.score, 2)) if media.score else None,
    )
