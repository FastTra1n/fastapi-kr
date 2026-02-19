import re

from pydantic import BaseModel, Field, field_validator

class User(BaseModel):
    name: str
    age: int

class FeedBack(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    message: str = Field(min_length=10, max_length=500)

    @field_validator('message', mode='after')
    @classmethod
    def validate_message(cls, message: str) -> str:
        if not((re.search(r'^(?!.*(кринж|рофл|вайб)).*$', message))):
            raise ValueError('Использование недопустимых слов')
        return message