from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from database import get_db_connection

class TaskCreate(BaseModel):
    title: str
    description: str

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None

app = FastAPI()

@app.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks (title, description) VALUES (?, ?)", (task.title, task.description)
    )
    conn.commit()
    
    id = cursor.lastrowid
    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?", (id,)
    )
    row = cursor.fetchone()
    conn.close()
    
    return TaskResponse(**row)

@app.get("/todo/{id}")
async def get_task(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?", (id, )
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found."
        )
    return TaskResponse(**row)

@app.patch("/todo/{id}")
async def update_task(id: int, task: TaskUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?", (id,)
    )
    row = cursor.fetchone()
    if row is None:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found."
        )
    
    updates = []
    params = []
    if task.title is not None:
        updates.append('title = ?')
        params.append(task.title)
    if task.description is not None:
        updates.append('description = ?')
        params.append(task.description)
    if task.completed is not None:
        updates.append('completed = ?')
        params.append(task.completed)
    if not updates:
        conn.close()
        return TaskResponse(**row)
    
    cursor.execute(
        f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?", (*params, id)
    )
    conn.commit()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    updated_row = cursor.fetchone()
    conn.close()
    return TaskResponse(**updated_row)

@app.delete("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?", (id,)
    )
    if cursor.fetchone() is None:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found."
        )
    
    cursor.execute(
        "DELETE FROM tasks WHERE id = ?", (id,)
    )
    conn.commit()
    conn.close()
