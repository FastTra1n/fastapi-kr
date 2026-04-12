import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pyrate_limiter import Duration, Limiter, Rate
from fastapi_limiter.depends import RateLimiter
import jwt
from passlib.context import CryptContext

from db import fake_topics, get_user_from_db, add_user_to_db, add_topic_to_db
from models import User, CurrentUser, Roles, Topic, TopicCreate, TopicUpdate
from rbac import PermissionChecker

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
        username = payload.get("sub")
        role = payload.get("role")
        return CurrentUser(username=username, role=role)
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

@app.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(1, Duration.MINUTE))))]
)
async def register(credentials: User):
    if get_user_from_db(credentials.username) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists."
        )
    hashed_password = pwd_context.hash(credentials.password)
    new_user = User(username=credentials.username, password=hashed_password, role=credentials.role)
    add_user_to_db(new_user)

    return {"message": "New user created!"}



@app.post(
    "/login",
    dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(5, Duration.MINUTE))))]
)
async def login(credentials: OAuth2PasswordRequestForm = Depends()):
    user = get_user_from_db(credentials.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    
    if not pwd_context.verify(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization failed."
        )
    
    token = create_jwt_token({"sub": user.username, "role": user.role})
    return {"access_token": token}

@app.get("/protected_resource")
@PermissionChecker(["admin"])
async def protected_resource(current_user: CurrentUser = Depends(get_user_from_token)):
    return {"message": f"Welcome back, {current_user.username}."}

@app.get("/topics")
async def get_topics():
    return fake_topics

@app.post("/topics", status_code=status.HTTP_201_CREATED)
@PermissionChecker(["user"])
async def create_topic(topic: TopicCreate, current_user: CurrentUser = Depends(get_user_from_token)):
    new_topic = Topic(
        title=topic.title,
        description=topic.description,
        creator=current_user.username
    )
    add_topic_to_db(new_topic)
    return {"message": "Created new post!"}

@app.patch("/topics/{id}")
@PermissionChecker(["user"])
async def update_topic(id: int, updated_topic: TopicUpdate, current_user: CurrentUser = Depends(get_user_from_token)):
    topic = fake_topics.get(id)
    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found."
        )
    if topic.creator != current_user.username and current_user.role != Roles.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="It's not your topic."
        )
    
    if updated_topic.title is not None:
        topic.title = updated_topic.title
    if updated_topic.description is not None:
        topic.description = updated_topic.description
    return {"message": "Topic updated"}

@app.delete("/topics/{id}", status_code=status.HTTP_204_NO_CONTENT)
@PermissionChecker(["admin"])
async def delete_topic(id: int, current_user: CurrentUser = Depends(get_user_from_token)):
    if id not in fake_topics:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    del fake_topics[id]