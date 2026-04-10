from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from passlib.context import CryptContext
import secrets

from config import settings
from db import get_user_from_db, add_user_to_db
from models import User, UserInDb

security = HTTPBasic()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def auth_docs(credentials: HTTPBasicCredentials = Depends(security)):
    is_correct_username = secrets.compare_digest(credentials.username, settings.docs_user)
    is_correct_password = secrets.compare_digest(credentials.password, settings.docs_password)
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"}
        )
    return credentials.username

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

if settings.mode == "DEV":
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    @app.get("/docs", include_in_schema=False)
    async def custom_docs(user: str = Depends(auth_docs)):
        return get_swagger_ui_html(openapi_url="/openapi.json", title="API Docs")
    
    @app.get("/openapi.json", include_in_schema=False)
    async def custom_openapi(user: str = Depends(auth_docs)):
        if not app.openapi_schema:
            app.openapi_schema = get_openapi(
                title="API Docs",
                version="1.0",
                routes=app.routes
            )
        return app.openapi_schema
elif settings.mode == "PROD":
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
else:
    raise ValueError(f"Incorrect mode: {settings.MODE}. Allowed modes: DEV, PROD.")

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
