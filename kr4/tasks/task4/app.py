import uuid

from fastapi import FastAPI, HTTPException, status

from models import UserRegister, UserResponse

app = FastAPI()

users = {}

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(credentials: UserRegister):
    for user in users.values():
        if user["username"] == credentials.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with the same username already exists."
            )
    user_id = str(uuid.uuid4())
    users[user_id] = {
        "id": user_id,
        "username": credentials.username,
        "password": credentials.password
    }
    return UserResponse(id=user_id, username=credentials.username)

@app.get("/users")
async def get_users():
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user_information(user_id: str):
    user = users.get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this id not found."
        )
    return UserResponse(id=user["id"], username=user["username"])

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str):
    if user_id not in users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this id not found."
        )
    del users[user_id]