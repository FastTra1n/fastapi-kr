from fastapi import FastAPI, status
from pydantic import BaseModel

from database import get_db_connection

class User(BaseModel):
    username: str
    password: str

app = FastAPI()

@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: User):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)", (user.username, user.password)
    )
    conn.commit()
    conn.close()

    return {"message": "User registered successfully!"}