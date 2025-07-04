import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

def get_openai_response(query:str) : 
    
    env_path = Path(__file__).resolve().parents[2] / '.env' # Gets the .env file that is 2 folders above the current file
    load_dotenv(dotenv_path=env_path)
    api_key = os.getenv("OPENAI_API_KEY")

    client = OpenAI(
        api_key=api_key
    )

    response = client.responses.create(
        model="gpt-4.1-nano",
        store=True,
        input=[
            {
                "role": "user",
                "content": query
            }
        ]
    )

    return response.output_text

def make_message(myString:str) :
    return {"message" : myString}