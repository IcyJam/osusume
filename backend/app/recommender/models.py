from datetime import datetime
from typing import Optional, List

from openai import BaseModel

from app.db.models import MediaType, Status


class ScoreRange(BaseModel):
    min: Optional[float]
    max: Optional[float]


class DateRange(BaseModel):
    start: Optional[datetime]
    end: Optional[datetime]


class TypeConstraints(BaseModel):
    included_types: List[MediaType]
    excluded_types: List[MediaType]


class StatusConstraints(BaseModel):
    included_statuses: List[Status]
    excluded_statuses: List[Status]


class RecommenderQueryHardConstraints(BaseModel):
    score_range: ScoreRange
    type: TypeConstraints
    date_range: DateRange
    status: StatusConstraints


class ProcessedRecommenderQuery(BaseModel):
    embedding_text: str
    keywords: List[str]
    hard_constraints: RecommenderQueryHardConstraints


class EmbeddedRecommenderQuery(BaseModel):
    vector: List[float]
