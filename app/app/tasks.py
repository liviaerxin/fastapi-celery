from celery import Celery
from celery.result import AsyncResult
import time
import os

BROKER_URL = os.environ.get("BROKER_URL", "redis://redis:6379")
RESULT_BACKEND = os.environ.get(
    "RESULT_BACKEND", "db+postgresql://postgres:example@postgresserver/db"
)

celery = Celery(
    "tasks",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    result_extended=True,  # return more fields than normal, seeing `TaskExtended` and `Task`
    task_track_started=True,
)

# Celery App Configuration
# use custom table names for the database result backend.
celery.conf.database_table_names = {
    "task": "myapp_taskmeta",
    "group": "myapp_groupmeta",
}

@celery.task(bind=True, name="create_short_task")
def create_short_task(self) -> bool:
    # self.update_state(state="PROGRESS")
    time.sleep(10)
    return True


@celery.task(name="create_medium_task")
def create_medium_task() -> bool:
    time.sleep(20)
    return True


@celery.task(name="create_long_task")
def create_long_task() -> bool:
    time.sleep(30)
    return True
