from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from enum import Enum
from pydantic import BaseModel
from typing import Any, Union
from .tasks import (
    create_short_task,
    create_medium_task,
    create_long_task,
    celery,
)
from pprint import pprint

app = FastAPI()

html_content = """
<html>
    <head>
        <title>Some HTML in here</title>
    </head>
    <body>
        <div class="starter-template">
        <h1>FastAPI + Celery + Docker</h1>
        <hr><br>
        <div>
            <h3>Tasks</h3>
            <p>Pick a task length.</p>
            <div class="btn-group" role="group" aria-label="Basic example">
            <button type="button" class="btn btn-primary" onclick="handleClick('short')">Short</a>
            <button type="button" class="btn btn-primary" onclick="handleClick('medium')">Medium</a>
            <button type="button" class="btn btn-primary" onclick="handleClick('long')">Long</a>
            </div>
        </div>
        <br><br>
        <div>
            <h3>Task Status</h3>
            <br>
            <table class="table">
            <thead>
                <tr>
                <th>ID</th>
                <th>Type</th>
                <th>Status</th>
                <th>Result</th>
                </tr>
            </thead>
            <tbody id="tasks">
            </tbody>
            </table>
        </div>
        </div>
    </body>
    <script type="text/javascript">
    (function() {
        console.log('Sanity Check!');
    })();

    function handleClick(type) {
    fetch('/tasks', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json'
        },
        body: JSON.stringify({ type: type }),
    })
    .then(response => response.json())
    .then(task => {
        getStatus(task.id)
    })
    }

    function getStatus(taskID) {
    fetch(`/tasks/${taskID}`, {
        method: 'GET',
        headers: {
        'Content-Type': 'application/json'
        },
    })
    .then(response => response.json())
    .then(task => {
        console.log(task)
        const html = `
        <tr>
            <td>${taskID}</td>
            <td>${task.type}</td>
            <td>${task.status}</td>
            <td>${task.result}</td>
        </tr>`;
        const newRow = document.getElementById('tasks').insertRow(0);
        newRow.innerHTML = html;

        const taskStatus = task.status;
        if (taskStatus === 'SUCCESS' || taskStatus === 'FAILURE') return false;
        setTimeout(function() {
        getStatus(task.id);
        }, 1000);
    })
    .catch(err => console.log(err));
    }
    </script>
</html>
"""


class TaskType(str, Enum):
    short = "short"
    medium = "medium"
    long = "long"


class TaskBase(BaseModel):
    type: Union[None, TaskType]


class TaskIn(TaskBase):
    pass


class Task(TaskBase):
    id: str
    status: str
    result: Union[None, Any]


@app.get("/", response_class=HTMLResponse)
async def read_index():
    return HTMLResponse(content=html_content, status_code=200)


@app.post("/tasks", status_code=201, response_model=Task)
def create_task(task: TaskIn):
    task_result: AsyncResult = None

    if task.type == TaskType.short:
        task_result = create_short_task.delay()
    if task.type == TaskType.medium:
        task_result = create_medium_task.delay()
    if task.type == TaskType.long:
        task_result = create_long_task.delay()

    # pprint(task_result)
    return Task(
        id=task_result.id,
        type=task.type,
        status=task_result.status,
        result=task_result.result,
    )


from celery.result import AsyncResult


@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: str):
    task_result = AsyncResult(task_id, app=celery)
    # task_result = app.AsyncResult(task_id)

    # PENDING (waiting for execution or unknown task id)
    # print(task_result.result)
    task_type = None
    if task_result.name:
        if task_result.name == create_short_task.name:
            task_type = TaskType.short
        if task_result.name == create_medium_task.name:
            task_type = TaskType.medium
        if task_result.name == create_long_task.name:
            task_type = TaskType.long

    if task_result.state == "SUCCESS":
        result = task_result.result
    else:
        result = None

    return Task(
        id=task_result.id,
        type=task_type,
        status=task_result.status,
        result=result,
    )
