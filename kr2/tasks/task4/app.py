from uuid import uuid4

from fastapi import FastAPI, Response, Cookie, HTTPException
from itsdangerous import URLSafeTimedSerializer, BadSignature

from models import User

app = FastAPI()

SECRET_TOKEN = URLSafeTimedSerializer('secret_key')

users = {}
sessions = {}

@app.post('/registration')
async def create_user(user: User):
    if users.get(user.username):
        raise HTTPException(status_code=400, detail="User with the same username already exists")
    
    new_user = {
        "id": str(uuid4()),
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
        user_id = user["id"]
        session_token = f'{user_id}.{SECRET_TOKEN.dumps(user_id)}' 
        sessions[session_token] = {"id": user["id"], "username": user["username"]}

        response.set_cookie(key="session_token", value=session_token, max_age=60, httponly=True)
        return {"session_token": session_token}
    else:
        raise HTTPException(status_code=401, detail="Incorrect credentials")

@app.get('/profile')
async def get_user(session_token: str | None = Cookie(None)):
    if not session_token:
        raise HTTPException(status_code=401, detail="Missing session token")
    
    try:
        user_id, signature = session_token.split('.', 1)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    try:
        signature_encoded = SECRET_TOKEN.loads(signature, max_age=60)
        if signature_encoded != user_id:
            raise HTTPException(status_code=401, detail="Invalid session token")
    except BadSignature:
        raise HTTPException(status_code=401, detail="Invalid token signature")

    for user in users.values():
        if user["id"] == user_id:
            return {"id": user["id"], "username": user["username"]}
    
    raise HTTPException(status_code=401, detail="User not found")