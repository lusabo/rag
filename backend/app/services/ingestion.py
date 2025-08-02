from typing import List
from io import BytesIO
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTTextBox, LTTextLine
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import File, Chunk
from app.services.chunker import chunk_text, clean_text
from app.services.embedder import get_embedder
from app.core.config import settings

def extract_text_by_page(pdf_bytes: bytes) -> List[str]:
    pages_text: List[str] = []
    for page_layout in extract_pages(BytesIO(pdf_bytes)):
        lines: List[str] = []
        for element in page_layout:
            if isinstance(element, (LTTextContainer, LTTextBox, LTTextLine)):
                text = element.get_text()
                if text:
                    lines.append(text)
        pages_text.append("\n".join(lines))
    return pages_text

def rough_token_count(s: str) -> int:
    return max(1, len(s.split()))

async def ingest_pdf(
    session: AsyncSession,
    filename: str,
    mime_type: str,
    pdf_bytes: bytes,
) -> File:
    # 1) salva o arquivo bruto
    f = File(filename=filename, mime_type=mime_type, content=pdf_bytes)
    session.add(f)
    await session.flush()  # f.id disponível

    # 2) extrai texto por página
    pages = extract_text_by_page(pdf_bytes)
    if not any(p.strip() for p in pages):
        raise ValueError("Não foi possível extrair texto do PDF.")

    # 3) chunking por página
    records: List[tuple[int, int, str]] = []  # (page_number, chunk_index, text)
    for pno, page_text in enumerate(pages, start=1):
        pieces = chunk_text(page_text)
        for idx, piece in enumerate(pieces):
            records.append((pno, idx, piece))

    # 4) embeddings em lote
    texts = [r[2] for r in records]
    embedder = get_embedder()
    vectors = await embedder.embed(texts)
    if any(len(v) != settings.embedding_dim for v in vectors):
        raise RuntimeError("Dimensão do embedding diferente de 1536.")

    # 5) persiste chunks
    for (pno, idx, piece), emb in zip(records, vectors):
        session.add(Chunk(
            file_id=f.id,
            page_number=pno,
            chunk_index=idx,
            text_cleaned=clean_text(piece),
            embedding=emb,
            token_count=rough_token_count(piece),
        ))

    await session.commit()
    await session.refresh(f)
    return f