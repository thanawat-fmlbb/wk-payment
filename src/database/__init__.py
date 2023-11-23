import os
from dotenv import load_dotenv
from sqlmodel import create_engine, SQLModel

from src.database import models

load_dotenv()

DATABASE_HOST = os.environ.get("DATABASE_HOST", "localhost")
DATABASE_PORT = os.environ.get("DATABASE_PORT", "5433")

DATABASE_NAME = os.environ.get("DATABASE_NAME", "postgres")
DATABASE_USERNAME = os.environ.get("DATABASE_USERNAME", "postgres")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD", "password")


def create_db_and_tables():
    postgres_url = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    engine = create_engine(postgres_url, echo=True)
    SQLModel.metadata.create_all(engine)


if __name__ == '__main__':
    create_db_and_tables()
