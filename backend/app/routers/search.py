from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_session
from app.schemas import SearchResponse, SearchHit
from app.services.search import semantic_search

router = APIRouter(prefix="/search", tags=["search"])

@router.get("", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=2),
    k: int = Query(5, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
):
    hits_raw = await semantic_search(session, q, k=k)
    hits = [SearchHit(**h) for h in hits_raw]
    return SearchResponse(query=q, hits=hits)