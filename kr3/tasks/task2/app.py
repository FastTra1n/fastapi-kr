from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext

from db import get_user_from_db, add_user_to_db
from models import User, UserInDb

app = FastAPI()
security = HTTPBasic()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def auth_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = get_user_from_db(credentials.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"}
        )
    
    if not pwd_context.verify(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"}
        )
    return user

@app.post("/register")
async def register(user: User):
    if get_user_from_db(user.username) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with that name already exists."
        )
    
    hashed_password = pwd_context.hash(user.password)
    new_user = UserInDb(username=user.username, hashed_password=hashed_password)
    add_user_to_db(new_user)
    
    return {"message": f"New user {user.username} created!"}
    
@app.get("/login")
async def login(user: UserInDb = Depends(auth_user)):
    return {"message": f"Welcome, {user.username}!"}