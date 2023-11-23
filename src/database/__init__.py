import os
from dotenv import load_dotenv
from sqlmodel import create_engine, SQLModel
import models

load_dotenv()
DATABASE_HOST = os.environ.get("DATABASE_HOST", "localhost:5433")
DATABASE_USERNAME = os.environ.get("DATABASE_USERNAME", "postgres")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD", "password")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "postgres")
DATABASE_URL = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"


def create_db_and_tables():
    engine = create_engine(DATABASE_URL, echo=True)
    SQLModel.metadata.create_all(engine)


if __name__ == '__main__':
    create_db_and_tables()
