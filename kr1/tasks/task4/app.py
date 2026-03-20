from fastapi import FastAPI

from models import User

app = FastAPI()
user = User(name="Никита Охотников", id=1)

@app.get('/users')
async def get_users():
    return {"name": user.name, "id": user.id}