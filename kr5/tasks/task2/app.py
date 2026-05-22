import os
from typing import Optional

from fastapi import FastAPI, Depends, Header, HTTPException, Query, status

from models import TaskCreate, TaskResponse, TaskStatusUpdate, StatusType

app = FastAPI()

db = {}
next_id = 1

def get_current_user_id(x_user_id: Optional[str] = Header(None)):
    if x_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-Id header is required"
        )
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-Id must be an integer"
        )
    return user_id

def get_task_or_404(task_id: int, user_id: int):
    task = db.get(task_id)
    if task is None or task["owner_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@app.get('/health')
def health_check():
    env = os.getenv("APP_ENV", "unknown")
    return {"status": "ok", "env": env}

@app.post('/tasks', response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task_data: TaskCreate, user_id: int = Depends(get_current_user_id)):
    global next_id

    new_task = task_data.model_dump()
    new_task["id"] = next_id
    new_task["owner_id"] = user_id
    db[next_id] = new_task
    next_id += 1
    return new_task

@app.get("/tasks", response_model=list[TaskResponse])
def get_list_tasks(user_id: int = Depends(get_current_user_id),
                   status: Optional[StatusType] = Query(None),
                   min_priority: Optional[int] = Query(None, ge=1, le=5)
                   ):
    user_tasks = [task for task in db.values() if task["owner_id"] == user_id]

    if status is not None:
        user_tasks = [task for task in user_tasks if task["status"] == status]
    if min_priority is not None:
        user_tasks = [task for task in user_tasks if task["priority"] >= min_priority]
    return user_tasks

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, user_id: int = Depends(get_current_user_id)):
    task = get_task_or_404(task_id, user_id)
    return task

@app.patch("/tasks/{task_id}/status", response_model=TaskResponse)
def update_task_status(new_status: TaskStatusUpdate,
                       task_id: int,
                       user_id: int = Depends(get_current_user_id)
                       ):
    task = get_task_or_404(task_id, user_id)
    task["status"] = new_status.status
    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, user_id: int = Depends(get_current_user_id)):
    task = get_task_or_404(task_id, user_id)
    del db[task_id]