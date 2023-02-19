from celery import Celery
from celery.result import AsyncResult
import time
import os

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://:6379")
print(CELERY_BROKER_URL)
celery = Celery(
    "tasks",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    result_extended=True,  # retrieve task name in `AsyncResult(task_id)`
    task_track_started=True,
)


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
