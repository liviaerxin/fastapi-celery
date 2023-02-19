from celery import Celery
from celery.result import AsyncResult
import time

celery = Celery(
    "tasks",
    broker="redis://localhost",
    backend="redis://localhost",
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
