from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from tqdm import tqdm

from app.services.openai_service import get_openai_embedding


def main():
    client = QdrantClient(host="qdrant", port=6333)

    documents = [
        {
            "name": "The Time Machine",
            "description": "A man travels through time and witnesses the evolution of humanity.",
            "author": "H.G. Wells",
            "year": 1895,
        },
        {
            "name": "Ender's Game",
            "description": "A young boy is trained to become a military leader in a war against an alien race.",
            "author": "Orson Scott Card",
            "year": 1985,
        },
        {
            "name": "Brave New World",
            "description": "A dystopian society where people are genetically engineered and conditioned to conform to a strict social hierarchy.",
            "author": "Aldous Huxley",
            "year": 1932,
        },
        {
            "name": "The Hitchhiker's Guide to the Galaxy",
            "description": "A comedic science fiction series following the misadventures of an unwitting human and his alien friend.",
            "author": "Douglas Adams",
            "year": 1979,
        },
        {
            "name": "Dune",
            "description": "A desert planet is the site of political intrigue and power struggles.",
            "author": "Frank Herbert",
            "year": 1965,
        },
        {
            "name": "Foundation",
            "description": "A mathematician develops a science to predict the future of humanity and works to save civilization from collapse.",
            "author": "Isaac Asimov",
            "year": 1951,
        },
        {
            "name": "Snow Crash",
            "description": "A futuristic world where the internet has evolved into a virtual reality metaverse.",
            "author": "Neal Stephenson",
            "year": 1992,
        },
        {
            "name": "Neuromancer",
            "description": "A hacker is hired to pull off a near-impossible hack and gets pulled into a web of intrigue.",
            "author": "William Gibson",
            "year": 1984,
        },
        {
            "name": "The War of the Worlds",
            "description": "A Martian invasion of Earth throws humanity into chaos.",
            "author": "H.G. Wells",
            "year": 1898,
        },
        {
            "name": "The Hunger Games",
            "description": "A dystopian society where teenagers are forced to fight to the death in a televised spectacle.",
            "author": "Suzanne Collins",
            "year": 2008,
        },
        {
            "name": "The Andromeda Strain",
            "description": "A deadly virus from outer space threatens to wipe out humanity.",
            "author": "Michael Crichton",
            "year": 1969,
        },
        {
            "name": "The Left Hand of Darkness",
            "description": "A human ambassador is sent to a planet where the inhabitants are genderless and can change gender at will.",
            "author": "Ursula K. Le Guin",
            "year": 1969,
        },
        {
            "name": "The Three-Body Problem",
            "description": "Humans encounter an alien civilization that lives in a dying system.",
            "author": "Liu Cixin",
            "year": 2008,
        },
    ]
    client.create_collection(
        collection_name="my_books",
        vectors_config=VectorParams(
            size=1536,  # Used model defines vector size
            distance=Distance.COSINE,
        ),
    )

    client.upload_points(
        collection_name="my_books",
        points=[
            PointStruct(id=idx, vector=get_openai_embedding(doc["description"]), payload=doc)
            for idx, doc in tqdm(enumerate(documents))
        ],
    )

    hits = client.query_points(
        collection_name="my_books",
        query=get_openai_embedding("alien invasion"),
        limit=3,
    ).points

    for hit in hits:
        print(hit.payload, "score:", hit.score)



if __name__ == "__main__":
    # main()
    pass
