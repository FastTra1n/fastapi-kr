from enum import Enum

from pydantic import BaseModel, Field

class Roles(str, Enum):
    USER: str = 'user'
    ADMIN: str = 'admin'

class User(BaseModel):
    username: str
    password: str
    role: Roles = Field(default=Roles.USER, validate_default=True)

class CurrentUser(BaseModel):
    username: str
    role: Roles

class Topic(BaseModel):
    title: str
    description: str
    creator: str

class TopicCreate(BaseModel):
    title: str
    description: str

class TopicUpdate(BaseModel):
    title: str | None = None
    description: str | None = None