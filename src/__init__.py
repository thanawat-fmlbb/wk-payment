import os

from celery import Celery
from src.database.engine import create_db_and_tables

create_db_and_tables()
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = os.environ.get("REDIS_PORT", "6381")
app = Celery("payment_service",
             broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/2",
             backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/3",
             broker_connection_retry_on_startup=True)

result_collector = Celery("payment_service",
             broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/4",
             backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/4",
             broker_connection_retry_on_startup=True)
