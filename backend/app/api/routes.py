from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.api.models import convert_media
from app.recommender.pipeline import get_recommendations
from app.services.openai_service import get_openai_response
from common.config.recommender.recommender_config import get_recommender_config


class QueryRequest(BaseModel):  # Helps validate the JSON structure
    query: str


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


@app.post("/recommend")
async def recommend(request: QueryRequest):
    recommendations = get_recommendations(request.query, get_recommender_config())
    recommendations_response = [convert_media(rec) for rec in recommendations]
    return {
        "message": " ; ".join(str(rec) for rec in recommendations_response)
    }
