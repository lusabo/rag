from pydantic import BaseModel
from typing import List

class FileOut(BaseModel):
    id: int
    filename: str
    mime_type: str
    created_at: str

class FileListOut(BaseModel):
    items: list[FileOut]
    total: int

class SearchHit(BaseModel):
    chunk_id: int
    file_id: int
    page_number: int
    chunk_index: int
    text: str
    score: float

class SearchResponse(BaseModel):
    query: str
    hits: List[SearchHit]