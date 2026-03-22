from uuid import uuid4
from datetime import datetime

from fastapi import FastAPI, Response, Cookie, HTTPException
from itsdangerous import URLSafeTimedSerializer, BadSignature

from models import User

app = FastAPI()

SECRET_TOKEN = URLSafeTimedSerializer('secret_key')

users = {}

def generate_session_token(user_id):
    timestamp = int(datetime.now().timestamp())
    data_to_signature = f"{user_id}.{timestamp}"
    signature = SECRET_TOKEN.dumps(data_to_signature)

    return f'{user_id}.{timestamp}.{signature}'

def verify_session_token(session_token):
    try:
        user_id, timestamp, signature = session_token.split('.', 2)
    except ValueError:
        return False
    
    try:
        signature_encoded = SECRET_TOKEN.loads(signature, max_age=300)
        encoded_user_id, encoded_timestamp = signature_encoded.split('.', 1)
        if encoded_user_id != user_id or encoded_timestamp != timestamp:
            return False
    except BadSignature:
        return False
    
    return user_id, timestamp

@app.post('/registration')
async def create_user(response: Response, user: User):
    if users.get(user.username):
        response.status_code = 400
        return {"message": "User with the same username already exists"}
    
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
        response.status_code = 404
        return {"message": "User was not found"}
    
    if user["password"] == credentials.password:
        session_token = generate_session_token(user["id"])

        response.set_cookie(key="session_token", value=session_token, max_age=300, httponly=True, secure=False)
        return {"session_token": session_token}
    else:
        response.status_code = 401
        return {"message": "Incorrect credentials"}

@app.get('/profile')
async def get_user(response: Response, session_token: str | None = Cookie(None)):
    if not session_token:
        response.status_code = 401
        return {"message": "Session expired"}
    
    validate = verify_session_token(session_token)
    if not validate:
        response.status_code = 401
        return {"message": "Invalid session"}

    user_id, timestamp = validate
    time_delta = int(datetime.now().timestamp()) - int(timestamp)

    if time_delta >= 300:
        response.status_code = 401
        return {"message": "Session expired"}
    
    if 180 <= time_delta < 300:
        fresh_session_token = generate_session_token(user_id)
        print("Updated token:", fresh_session_token)
        response.set_cookie(key="session_token", value=fresh_session_token, max_age=300, httponly=True, secure=False)

    for user in users.values():
        if user["id"] == user_id:
            return {"id": user["id"], "username": user["username"]}
    
    response.status_code = 401
    return {"message": "Invalid session"}