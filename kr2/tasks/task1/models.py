from pydantic import BaseModel, EmailStr, Field
from typing import Annotated, Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: Annotated[int, Field(gt=0)] = None
    is_subscribed: Optional[bool] = None