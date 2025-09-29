import datetime
import random

from app.db.models import MediaType
from app.recommender.models import ProcessedRecommenderQuery, RecommenderQueryHardConstraints, ScoreRange, \
    TypeConstraints, DateRange, StatusConstraints, EmbeddedRecommenderQuery
from app.recommender.retriever import retrieve_top_k
from app.vector_db.vector_database import vector_database_client

if __name__ == '__main__':

    test_embed = [random.random() for _ in range(1536)]

    test_processed_query = ProcessedRecommenderQuery(
        embedding_text="test",
        keywords=["test"],
        hard_constraints=RecommenderQueryHardConstraints(
            score_range=ScoreRange(min=None, max=8.5),
            type=TypeConstraints(included_types=[MediaType("MANGA")], excluded_types=[]),
            date_range=DateRange(start=datetime.datetime(1999, 1, 1), end=None),
            status=StatusConstraints(included_statuses=[], excluded_statuses=[])
        )
    )

    test_embedded_query = EmbeddedRecommenderQuery(vector=test_embed)

    print(
        retrieve_top_k(
            embedded_query=test_embedded_query,
            processed_query=test_processed_query,
            client=vector_database_client,
            k=5,
        )
    )
