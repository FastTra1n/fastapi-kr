from fastapi import FastAPI

from models import UserCreate

app = FastAPI()

users = []

@app.get('/users')
async def get_users():
    return users

@app.post('/create_user', response_model=UserCreate)
async def create_user(user: UserCreate):
    new_user = {
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "is_subscribed": user.is_subscribed
    }
    users.append(new_user)
    return new_user