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

def get_openai_embedding(text:str) -> list[float]:
    response = openai_client.get_embedding(text)
    return response