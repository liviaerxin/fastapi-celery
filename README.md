# FastAPI and Celery

```sh
uvicorn app.main:app --reload
```

```sh
celery --app app.tasks:celery worker --loglevel=info
```
