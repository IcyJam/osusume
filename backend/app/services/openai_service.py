import json
import re
from typing import List
import tiktoken
from tqdm import tqdm

from app.clients.openai_client import openai_client
from common.env import get_env_variable


class QueryValidationError(Exception):
    """Raised when the user query is invalid."""
    pass


class QueryTooLongError(Exception):
    """Raised when the user query is too long."""
    pass


class LLMResponseError(Exception):
    """Raised when the LLM response is problematic."""
    pass


def make_message(my_string: str):
    return {"message": my_string}


def get_openai_response(query: str):
    if len(query) > 500:
        return make_message("Sorry, your query was too long! Try to make it a bit shorter.")

    else:

        response = openai_client.get_response(
            prompt=query,
            instructions="Generate a concise output (200 maximum), not using any formatting so that it displays properly in an external app. Only reply to the query, without any form of introduction."
        )

        return make_message(response.output_text)


def get_embedding(text: str, model, dimensions) -> List[float]:
    response = openai_client.get_embedding(
        text=text,
        model=model,
        dimensions=dimensions,
    )
    return response


def get_embeddings(texts: List[str], model: str, dimensions: int) -> List[List[float]]:
    max_tokens_per_batch = 8192
    tokenizer = tiktoken.encoding_for_model(model)

    # Estimate token count for each text
    token_counts = [len(tokenizer.encode(text)) for text in texts]

    embeddings = []
    current_batch = []
    current_token_count = 0

    for text, token_count in tqdm(zip(texts, token_counts), desc="Embedding texts", total=len(texts)):
        # If adding this text exceeds the max, flush the current batch before adding this text
        if current_token_count + token_count > max_tokens_per_batch and current_batch:
            tqdm.write(f"Sending batch of {len(current_batch)} texts with ~{current_token_count} tokens")
            batch_embeddings = openai_client.get_embeddings_batched(
                texts=current_batch,
                model=model,
                dimensions=dimensions,
                batch_size=len(current_batch),
            )
            embeddings.extend(batch_embeddings)
            current_batch = []
            current_token_count = 0

        current_batch.append(text)
        current_token_count += token_count

    # Handle the final batch
    if current_batch:
        tqdm.write(f"Sending final batch of {len(current_batch)} texts with ~{current_token_count} tokens")
        batch_embeddings = openai_client.get_embeddings_batched(
            texts=current_batch,
            model=model,
            dimensions=dimensions,
            batch_size=len(current_batch),
        )
        embeddings.extend(batch_embeddings)

    return embeddings


def sanitize_llm_query(query: str) -> str:
    """
    Sanitize and validate a user query before sending it to the LLM.

    :param query: Raw user query.
    :return: Cleaned and safe query string.
    :raises QueryValidationError: If the query is empty or invalid.
    """
    if not isinstance(query, str):
        raise QueryValidationError("Query must be a string.")

    # Trim whitespace and limit length
    maximum_query_length = 500
    query = query.strip()
    if not query:
        raise QueryValidationError("Query is empty after trimming.")
    if len(query) > maximum_query_length:
        raise QueryTooLongError(f"Query is too long: {len(query)}. Maximum length is {maximum_query_length}.")

    # Remove control/non-printable characters
    query = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', query)

    # Filter basic prompt injection patterns
    forbidden_patterns = [r"(?i)ignore\s+previous", r"(?i)system\s*:", r"(?i)assistant\s*:"]
    if any(re.search(p, query) for p in forbidden_patterns):
        raise QueryValidationError("Query contains forbidden instructions.")

    query = re.sub(r'\s+', ' ', query)

    return query


def get_processed_recommender_query(user_query):
    try:
        clean_query = sanitize_llm_query(user_query)
        prompt_id = get_env_variable("QUERY_PROCESSING_PROMPT_ID")
        response = openai_client.get_response_from_prompt_id(user_input=clean_query, prompt_id=prompt_id)

        try:
            response_dict = json.loads(response.strip())
            return response_dict
        except json.JSONDecodeError as e:
            raise LLMResponseError(f"Failed to parse JSON from LLM response: {response}. Exception: {e}")

    except (QueryValidationError, LLMResponseError) as e:
        return f"Error while processing user query: {str(e)}"
    except Exception as e:
        # Catch-all to avoid unhandled server errors
        return f"Unexpected error: {str(e)}"
