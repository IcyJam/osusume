import openai
from openai import OpenAI
from common.env import get_env_variable


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

    def get_embedding(self, text: str) -> list[float]: # single embedding
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding


# Singleton instance
openai_api_key = get_env_variable("OPENAI_API_KEY")
openai_client = OpenAIClient(openai_api_key)
