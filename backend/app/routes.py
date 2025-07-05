import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[0]))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from clients.openai_client import get_openai_response

class QueryRequest(BaseModel):      # Helps validate the JSON structure
    query:str

app = FastAPI()

origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/chat")
async def generate_response(request: QueryRequest):
    return get_openai_response(request.query)