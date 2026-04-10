from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    mode: str = Field(..., env="MODE")
    docs_user: str = Field(..., env="DOCS_USER")
    docs_password: str = Field(..., env="DOCS_PASSWORD")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()