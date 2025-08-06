from typing import List, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.embedder import get_embedder

SQL = """
SELECT
  c.id           AS chunk_id,
  c.file_id      AS file_id,
  c.page_number  AS page_number,
  c.chunk_index  AS chunk_index,
  c.text_cleaned AS content,
  (c.embedding <-> (:qvec)::float4[]::vector) AS l2_dist
FROM chunks c
ORDER BY c.embedding <-> (:qvec)::float4[]::vector
LIMIT :k;
"""

_embedder = None

async def semantic_search(session: AsyncSession, query: str, k: int = 5) -> List[Dict[str, Any]]:
    global _embedder
    if _embedder is None:
        _embedder = get_embedder()

    # 1) embedding da pergunta (list[float])
    qvec = (await _embedder.embed([query]))[0]

    # 2) consulta com CAST do parâmetro para vector
    rows = (
        await session.execute(text(SQL), {"qvec": qvec, "k": k})
    ).mappings().all()

    # 3) saída normalizada
    return [
        {
            "chunk_id": r["chunk_id"],
            "file_id": r["file_id"],
            "page_number": r["page_number"],
            "chunk_index": r["chunk_index"],
            "text": r["content"],
            "score": float(r["l2_dist"]),
        }
        for r in rows
    ]
