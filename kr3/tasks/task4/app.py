import datetime
from fastapi import FastAPI, Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import jwt

from db import get_user_from_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = 'secret_key'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 15

app = FastAPI()

def create_jwt_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.now() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user_from_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The access token has expired."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token."
        )

@app.post("/login")
async def login(credentials: OAuth2PasswordRequestForm = Depends()):
    user = get_user_from_db(credentials.username)
    if user and credentials.password == user.password:
        token = create_jwt_token({"sub": user.username})
        return {"access_token": token}
    
    raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials."
        )

@app.get("/protected_resource")
async def protected_resource(user: str = Depends(get_user_from_token)):
    return {"message": f"Welcome back, {user}."}