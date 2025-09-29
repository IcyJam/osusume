import pytest

from app.db.models import MediaType, Status
from app.recommender.embedder import embed_processed_query
from app.recommender.models import ProcessedRecommenderQuery, RecommenderQueryHardConstraints, ScoreRange, \
    TypeConstraints, DateRange, StatusConstraints, EmbeddedRecommenderQuery


@pytest.fixture
def sample_processed_query():
    return ProcessedRecommenderQuery(
        embedding_text="An anime with action and adventure",
        keywords=["adventure", "action"],
        hard_constraints=RecommenderQueryHardConstraints(
            score_range=ScoreRange(min=7.0, max=9.0),
            type=TypeConstraints(included_types=[MediaType.TV], excluded_types=[]),
            date_range=DateRange(start=None, end=None),
            status=StatusConstraints(included_statuses=[Status.FINISHED], excluded_statuses=[])
        )
    )


def test_embed_processed_query(monkeypatch, sample_processed_query):
    # Mock get_embedding
    def fake_embedding(text, model, dimensions):
        # Ensure combined text includes sorted keywords
        assert "action" in text
        assert "adventure" in text
        return [0.1, 0.2, 0.3]

    monkeypatch.setattr("app.recommender.embedder.get_embedding", fake_embedding)

    result = embed_processed_query(query=sample_processed_query, model="model", dimensions=3)

    # Assertions
    assert isinstance(result, EmbeddedRecommenderQuery)
    assert result.vector == [0.1, 0.2, 0.3]
