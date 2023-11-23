from celery import Celery
from src.database import create_db_and_tables

create_db_and_tables()
app = Celery("payment_service",
             broker="redis://localhost:6381/0",
             backend="redis://localhost:6381/0",
             broker_connection_retry_on_startup=True)
