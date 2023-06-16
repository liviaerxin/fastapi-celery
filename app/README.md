# FastAPI and Celery

Python ">=3.10"

```sh
uvicorn app.main:app --reload


```

```sh
celery --app app.tasks:celery worker --loglevel=info
```
