from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

class FeedBack(BaseModel):
    name: str
    message: str