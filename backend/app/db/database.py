from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from common.env import get_env_variable


def get_database_url():
    db_user = get_env_variable("POSTGRES_USER")
    db_password = get_env_variable("POSTGRES_PASSWORD")
    db_host = "db"  # name of the docker service that runs the database
    db_port = 5432
    db_name = get_env_variable("POSTGRES_DB")

    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    return database_url


DATABASE_URL = get_database_url()

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
