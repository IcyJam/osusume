import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


def make_message(my_string: str):
    return {"message": my_string}


def get_openai_response(query: str):
    if len(query) > 500:
        return make_message("Sorry, your query was too long! Try to make it a bit shorter.")

    else:
        env_path = Path(__file__).resolve().parents[
                       2] / '.env'  # Gets the .env file that is 2 folders above the current file
        load_dotenv(dotenv_path=env_path)
        api_key = os.getenv("OPENAI_API_KEY")

        client = OpenAI(
            api_key=api_key
        )

        response = client.responses.create(
            model="gpt-4.1-nano",
            instructions="Generate a concise output (200 maximum), not using any formatting so that it displays properly in an external app. Only reply to the query, without any form of introduction.",
            store=True,
            input=[
                {
                    "role": "user",
                    "content": query
                },
            ]
        )

        return make_message(response.output_text)
