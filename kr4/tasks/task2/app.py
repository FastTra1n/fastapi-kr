from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI()

class CustomExceptionA(HTTPException):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail=detail)

class CustomExceptionB(HTTPException):
    def __init__(self, detail: str, status_code: int = 404):
        super().__init__(status_code=status_code, detail=detail)


@app.exception_handler(CustomExceptionA)
async def custom_exception_a_handler(request: Request, exc: CustomExceptionA):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(CustomExceptionB)
async def custom_exception_b_handler(request: Request, exc: CustomExceptionB):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.get("/validate/{value}")
async def validate_value(value: int):
    if value < 0:
        raise CustomExceptionA(detail=f"Value {value} is negative.", status_code=400)
    return {"message": f"Value {value} is valid."}

@app.get("/recourse/{recourse_id}")
async def get_recourse(recourse_id: int):
    if recourse_id == 42:
        raise CustomExceptionB(detail=f"Recourse with id {recourse_id} not found.", status_code=404)
    return {"message": f"Information about recourse with id {recourse_id}."}