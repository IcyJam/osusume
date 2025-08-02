from app.recommender.models import ProcessedRecommenderQuery, EmbeddedRecommenderQuery
from app.services.openai_service import get_embedding
from common.env import get_env_variable


def embed_processed_query(query: ProcessedRecommenderQuery) -> EmbeddedRecommenderQuery:
    sorted_keywords = sorted(query.keywords)
    combined_text = query.embedding_text + ", " + ", ".join(sorted_keywords)
    embedding = get_embedding(
        text=combined_text,
        model=get_env_variable("EMBEDDING_MODEL"),
        dimensions=int(get_env_variable("EMBEDDING_DIMENSIONS")),
    )

    return EmbeddedRecommenderQuery(
        vector=embedding,
    )
