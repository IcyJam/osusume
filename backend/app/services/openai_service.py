from typing import List
import tiktoken
from tqdm import tqdm

from app.clients.openai_client import openai_client


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