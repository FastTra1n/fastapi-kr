from fastapi import FastAPI, Response, Cookie, HTTPException
from uuid import uuid4

from models import User

app = FastAPI()

users = {}
sessions = {}

@app.post('/registration')
async def create_user(user: User):
    if users.get(user.username):
        raise HTTPException(status_code=400, detail="User with the same username already exists")
    
    new_user = {
        "username": user.username,
        "password": user.password
    }
    users[user.username] = new_user
    return new_user

@app.post('/login')
async def auth_user(response: Response, credentials: User):
    user = users.get(credentials.username)
    if not user:
        raise HTTPException(status_code=404, detail="User was not found")
    
    if user["password"] == credentials.password:
        session_token = str(uuid4())
        sessions[session_token] = credentials.username

        response.set_cookie(key="session_token", value=session_token, max_age=3600, httponly=True)
        return {"session_token": session_token}
    else:
        raise HTTPException(status_code=401, detail="Incorrect credentials")

@app.get('/user')
async def get_user(session_token: str | None = Cookie(None)):
    if not session_token:
        raise HTTPException(status_code=401, detail="Missing session token")
    
    username = sessions.get(session_token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired session token")
    
    return {"username": username}