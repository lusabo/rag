from fastapi import FastAPI
from app.routers import files, search

app = FastAPI(title="PDF Vector Search API", version="0.1.0")
app.include_router(files.router)
app.include_router(search.router)

@app.get("/health")
def health():
    return {"status": "ok"}