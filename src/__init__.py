import os

from celery import Celery
from src.database import create_db_and_tables

create_db_and_tables()
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = os.environ.get("REDIS_PORT", "6381")
app = Celery("payment_service",
             broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
             backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
             broker_connection_retry_on_startup=True)