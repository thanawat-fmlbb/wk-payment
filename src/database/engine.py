import os
from dotenv import load_dotenv
from sqlmodel import create_engine, SQLModel

from src.database import models


def get_engine():
    load_dotenv()

    db_host = os.environ.get("DATABASE_HOST", "localhost")
    db_port = os.environ.get("DATABASE_PORT", "5433")

    db_username = os.environ.get("DATABASE_USERNAME", "postgres")
    db_password = os.environ.get("DATABASE_PASSWORD", "password")
    postgres_url = (f"postgresql://"
                    f"{db_username}:{db_password}@"
                    f"{db_host}:{db_port}/payment")
    engine = create_engine(postgres_url, echo=True)
    return engine


def create_db_and_tables():
    engine = get_engine()
    SQLModel.metadata.create_all(engine)


if __name__ == '__main__':
    create_db_and_tables()
