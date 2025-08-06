import io
from typing import List
from pypdf import PdfReader
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.embedder import get_embedder
from app.models import File, Chunk
from app.core.config import settings

def chunk_text(text: str, max_chars: int = 1000, overlap: int = 200):
    i, n = 0, len(text)
    while i < n:
        yield text[i:i+max_chars]
        i += max_chars - overlap

async def ingest_pdf(session: AsyncSession, filename: str, mime_type: str, data: bytes) -> File:
    f = File(filename=filename, mime_type=mime_type, data=data)  # se você salva o PDF bruto na tabela
    session.add(f)
    await session.flush()  # f.id disponível

    reader = PdfReader(io.BytesIO(data))
    chunk_payload: List[tuple[int,int,str]] = []
    for page_no, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        for j, ch in enumerate(chunk_text(text)):
            chunk_payload.append((page_no, j, ch))

    if not chunk_payload:
        await session.commit()
        return f

    embedder = get_embedder()
    # batch embeddings
    texts = [c[2] for c in chunk_payload]
    embeds = await embedder.embed(texts)

    chunks = [
        Chunk(
            file_id=f.id,
            page_number=page_no,
            chunk_index=idx,
            text_cleaned=txt,
            embedding=vec,        # list[float] – OK se sua coluna é VECTOR(1536/3072) com pgvector
            token_count=len(txt),
        )
        for (page_no, idx, txt), vec in zip(chunk_payload, embeds)
    ]
    session.add_all(chunks)
    await session.commit()
    return f
