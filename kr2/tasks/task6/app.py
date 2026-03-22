import re

from fastapi import FastAPI, Header, HTTPException

app = FastAPI()

@app.get('/headers')
async def get_headers(
    user_agent: str | None = Header(None),
    accept_language: str | None = Header(None)
    ):
    if not user_agent or not accept_language:
        raise HTTPException(status_code=400, detail="Missing required headers")
    
    pattern = r'^([a-zA-Z*]+(-[a-zA-Z*]+)?(;q=[01]\.\d{1,3})?)(,([a-zA-Z*]+(-[a-zA-Z*]+)?(;q=[01]\.\d{1,3})?))*$'
    if not re.match(pattern, accept_language):
        raise HTTPException(status_code=400, detail="Bad \"Accept-Language\" header")

    return {"User-Agent": user_agent, "Accept-Language": accept_language}