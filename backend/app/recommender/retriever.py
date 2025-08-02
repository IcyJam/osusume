from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.fastembed_common import QueryResponse
from qdrant_client.http.models import MatchValue, FieldCondition, Range, Filter, DatetimeRange

from app.recommender.models import EmbeddedRecommenderQuery, ProcessedRecommenderQuery, RecommenderQueryHardConstraints
from app.vector_db.vector_database import DEFAULT_MEDIA_COLLECTION_NAME


def build_filter_from_constraints(
        constraints: RecommenderQueryHardConstraints
) -> Optional[Filter]:
    must_clauses = []
    must_not_clauses = []
    should_clauses = []

    # Score range filter
    score_min = constraints.score_range.min
    score_max = constraints.score_range.max
    if score_min is not None or score_max is not None:
        must_clauses.append(
            FieldCondition(
                key="score",
                range=Range(
                    gte=score_min if score_min is not None else None,
                    lte=score_max if score_max is not None else None,
                ),
            )
        )

    # Type filter (include + exclude)
    type_include = constraints.type.included_types
    type_exclude = constraints.type.excluded_types

    if type_include:
        should_clauses.extend(
            [
                FieldCondition(
                    key="type",
                    match=MatchValue(value=t.value)
                )
                for t in type_include
            ]
        )

    if type_exclude:
        must_not_clauses.extend(
            [
                FieldCondition(
                    key="type",
                    match=MatchValue(value=t.value)
                )
                for t in type_exclude
            ]
        )

    # Date range filter
    date_start = constraints.date_range.start
    date_end = constraints.date_range.end
    if date_start is not None or date_end is not None:
        must_clauses.append(
            FieldCondition(
                key="start_date",
                range=DatetimeRange(
                    gte=date_start.isoformat() if date_start else None,
                    lte=date_end.isoformat() if date_end else None,
                )
            )
        )

    # Status filter (include + exclude)
    status_include = constraints.status.included_statuses
    status_exclude = constraints.status.excluded_statuses

    if status_include:
        should_clauses.extend(
            [
                FieldCondition(
                    key="status",
                    match=MatchValue(value=s.value)
                )
                for s in status_include
            ]
        )
    if status_exclude:
        must_not_clauses.extend(
            [
                FieldCondition(
                    key="status",
                    match=MatchValue(value=s.value)
                )
                for s in status_exclude
            ]
        )

    if not (must_clauses or must_not_clauses or should_clauses):
        return None

    return Filter(
        must=must_clauses,
        must_not=must_not_clauses,
        should=should_clauses,
    )


def retrieve_top_k(
        embedded_query: EmbeddedRecommenderQuery,
        processed_query: ProcessedRecommenderQuery,
        client: QdrantClient,
        k: int
) -> QueryResponse:
    """
    Retrieve the top-k closest vectors to the embedded query from Qdrant,
    applying filtering based on processed query's hard constraints.
    """
    vdb_filter = build_filter_from_constraints(processed_query.hard_constraints)

    response = client.query_points(
        collection_name=DEFAULT_MEDIA_COLLECTION_NAME,
        query=embedded_query.vector,
        limit=k,
        query_filter=vdb_filter
    )
    return response
