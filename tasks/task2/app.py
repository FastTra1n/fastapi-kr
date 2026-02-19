from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()

@app.get('/')
async def root():
    page = 'index.html'
    return FileResponse(page)