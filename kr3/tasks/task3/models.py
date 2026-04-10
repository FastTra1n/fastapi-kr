from pydantic import BaseModel

class UserBase(BaseModel):
    username: str

class User(UserBase):
    password: str

class UserInDb(UserBase):
    hashed_password: str
