import re

from pydantic import BaseModel, field_validator

class CommonHeaders(BaseModel):
    user_agent: str | None = None
    accept_language: str | None = None

    @field_validator('accept_language', mode='after')
    @classmethod
    def validate_accept_language(cls, accept_language):
        pattern = r'^([a-zA-Z*]+(-[a-zA-Z*]+)?(;q=[01]\.\d{1,3})?)(,([a-zA-Z*]+(-[a-zA-Z*]+)?(;q=[01]\.\d{1,3})?))*$'
        if not re.match(pattern, accept_language):
            raise ValueError('Bad "Accept-Language" header')
        return accept_language