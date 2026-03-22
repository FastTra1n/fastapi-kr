import json
from datetime import datetime

from fastapi import FastAPI, Response, Header, HTTPException

from models import CommonHeaders

app = FastAPI()

@app.get('/headers')
async def get_headers(headers: CommonHeaders = Header()):
    if headers.user_agent is None or headers.accept_language is None:
        raise HTTPException(status_code=400, detail="Missing required headers")
    return {"User-Agent": headers.user_agent, "Accept-Language": headers.accept_language}

@app.get('/info')
async def show_info(response: Response, headers: CommonHeaders = Header()):
    if headers.user_agent is None or headers.accept_language is None:
        raise HTTPException(status_code=400, detail="Missing required headers")
    
    data = {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language
        }
    }
    response.headers["X-Server-Time"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S") # 2025-04-16T12:34:56
    return data