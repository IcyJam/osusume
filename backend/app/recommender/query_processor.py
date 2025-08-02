from datetime import datetime
from typing import Dict, Any

from app.db.models import MediaType, Status
from app.recommender.models import ScoreRange, TypeConstraints, DateRange, StatusConstraints, \
    RecommenderQueryHardConstraints, ProcessedRecommenderQuery
from app.services.openai_service import get_processed_recommender_query


# --- Converter functions ---

def parse_score_range(data: Dict[str, Any]) -> ScoreRange:
    return ScoreRange(min=data["min"], max=data["max"])


def parse_type_constraints(data: Dict[str, Any]) -> TypeConstraints:
    return TypeConstraints(
        included_types=[MediaType[t] for t in data["include"]],
        excluded_types=[MediaType[t] for t in data["exclude"]],
    )


def parse_date_range(data: Dict[str, Any]) -> DateRange:
    date_format = "%Y-%m"
    start = datetime.strptime(data["start"], date_format) if data.get("start") else None
    end = datetime.strptime(data["end"], date_format) if data.get("end") else None
    return DateRange(start=start, end=end)


def parse_status_constraints(data: Dict[str, Any]) -> StatusConstraints:
    return StatusConstraints(
        included_statuses=[Status[s] for s in data["include"]],
        excluded_statuses=[Status[s] for s in data["exclude"]],
    )


def parse_hard_constraints(data: Dict[str, Any]) -> RecommenderQueryHardConstraints:
    return RecommenderQueryHardConstraints(
        score_range=parse_score_range(data["score_range"]),
        type=parse_type_constraints(data["type"]),
        date_range=parse_date_range(data["date_range"]),
        status=parse_status_constraints(data["status"]),
    )


# --- Main function ---

def process_query(user_query) -> ProcessedRecommenderQuery:
    raw_query = get_processed_recommender_query(user_query)
    return ProcessedRecommenderQuery(
        embedding_text=raw_query["embedding_text"],
        keywords=raw_query["keywords"],
        hard_constraints=parse_hard_constraints(raw_query["hard_constraints"])
    )
