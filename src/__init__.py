import os
from dotenv import load_dotenv
from celery import Celery

load_dotenv()
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = os.environ.get("REDIS_PORT", "6381")
app = Celery("payment_service",
             broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/1",
             backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/1",
             broker_connection_retry_on_startup=True)

result_collector = Celery("payment_service",
             broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/4",
             backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/4",
             broker_connection_retry_on_startup=True)

from .database.models import UserMoney, PaymentInfo
from .database.engine import create_db_and_tables
create_db_and_tables()
