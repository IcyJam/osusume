from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
async def read_root():
    return {"message": "Hi there, my name is Yappi and I'm going to help you find the anime of your dreams :D"}

