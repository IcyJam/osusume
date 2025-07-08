from openai import OpenAI

from common.env import get_env_variable


def make_message(my_string: str):
    return {"message": my_string}


def get_openai_response(query: str):
    if len(query) > 500:
        return make_message("Sorry, your query was too long! Try to make it a bit shorter.")

    else:
        api_key = get_env_variable("OPENAI_API_KEY")

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
