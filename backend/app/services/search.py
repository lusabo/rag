from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.services.embedder import get_embedder

SQL = """
SELECT
  c.id AS chunk_id,
  c.file_id AS file_id,
  c.page_number AS page_number,
  c.chunk_index AS chunk_index,
  c.text_cleaned AS text_cleaned,
  (c.embedding <-> :qvec) AS l2_dist
FROM chunks c
ORDER BY c.embedding <-> :qvec
LIMIT :k;
"""

def dist_to_score(d: float) -> float:
    return 1.0 / (1.0 + d)

async def semantic_search(session: AsyncSession, query: str, k: int = 5):
    embedder = get_embedder()
    qvec = (await embedder.embed([query]))[0]
    rows = (await session.execute(text(SQL), {"qvec": qvec, "k": k})).mappings().all()
    return [
        {
            "chunk_id": r["chunk_id"],
            "file_id": r["file_id"],
            "page_number": r["page_number"],
            "chunk_index": r["chunk_index"],
            "text": r["text_cleaned"],
            "score": float(dist_to_score(r["l2_dist"])),
        }
        for r in rows
    ]