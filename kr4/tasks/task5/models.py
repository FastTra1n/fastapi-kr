from pydantic import BaseModel

class UserRegister(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str