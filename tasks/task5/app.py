from fastapi import FastAPI

from models import User

app = FastAPI()
users = []

def is_adult(age):
    return age >= 18

@app.get('/users')
async def get_users():
    return users

@app.post('/user')
async def create_user(user: User):
    new_user = {"name": user.name, "age": user.age, "is_adult": is_adult(user.age)}
    users.append(new_user)
    return new_user