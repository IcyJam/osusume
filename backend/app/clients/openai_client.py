import time
from typing import List

import math
import openai
from openai import OpenAI
from tqdm import tqdm

from common.env import get_env_variable

MAXIMUM_EMBEDDING_REQUESTS_PER_MINUTE = 2500  # actual is 3000, lowered for safety https://platform.openai.com/settings/organization/limits


class OpenAIClient:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def get_response(self, prompt: str, instructions: str):
        response = self.client.responses.create(
            model="gpt-4.1-nano",
            instructions=instructions,
            store=True,
            input=[{"role": "user", "content": prompt}]
        )
        return response

    def get_response_from_prompt_id(self, user_input: str, prompt_id: str):
        response = self.client.responses.create(
            prompt={"id": prompt_id},
            input=user_input
        )
        return response.output[0].content[0].text

    def get_embedding(self, text: str, model, dimensions) -> list[float]:  # single embedding
        response = self.client.embeddings.create(
            model=model,
            input=text,
            dimensions=dimensions
        )
        return response.data[0].embedding

    def get_embeddings_batched(
            self,
            texts: List[str],
            model: str,
            dimensions: int,
            batch_size: int = 256,
            sleep_time: float = 0.5,
            max_retries: int = 3,
    ) -> List[List[float]]:
        all_embeddings = []
        total = len(texts)
        num_batches = math.ceil(total / batch_size)

        for i in range(num_batches):
            start = i * batch_size
            end = min(start + batch_size, total)
            batch_texts = texts[start:end]

            for attempt in range(max_retries):
                try:
                    response = self.client.embeddings.create(
                        model=model,
                        input=batch_texts,
                        dimensions=dimensions,
                    )
                    batch_embeddings = [item.embedding for item in response.data]
                    all_embeddings.extend(batch_embeddings)
                    break  # Success, break retry loop
                except Exception as e:
                    print(f"Batch {i + 1}/{num_batches} failed on attempt {attempt + 1}: {e}")
                    time.sleep(2 ** attempt)
            else:
                raise RuntimeError(f"Batch {i + 1} failed after {max_retries} retries.")

            if sleep_time > 0 and i < num_batches - 1:
                time.sleep(sleep_time)

        return all_embeddings


# Singleton instance
openai_api_key = get_env_variable("OPENAI_API_KEY")
openai_client = OpenAIClient(openai_api_key)
