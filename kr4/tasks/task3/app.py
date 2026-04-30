from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from models import User

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def credentials_validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": "Validation error", "errors": exc.errors()}
    )

@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: User):
    return {"message": f"User {user.username} created successfully!"}