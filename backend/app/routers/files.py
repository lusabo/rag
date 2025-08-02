from fastapi import APIRouter, UploadFile, File as F, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.db import get_session
from app.models import File
from app.schemas import FileOut, FileListOut
from app.core.config import settings
from app.services.ingestion import ingest_pdf

router = APIRouter(prefix="/files", tags=["files"])

@router.post("/upload", response_model=FileOut, status_code=201)
async def upload_pdf(
    upload: UploadFile = F(..., description="PDF para indexar"),
    session: AsyncSession = Depends(get_session),
):
    if upload.content_type != "application/pdf":
        raise HTTPException(400, "Apenas PDFs são aceitos.")
    data = await upload.read()
    if len(data) / (1024 * 1024) > settings.max_upload_mb:
        raise HTTPException(413, f"Arquivo acima de {settings.max_upload_mb}MB.")
    try:
        f = await ingest_pdf(session, upload.filename, upload.content_type, data)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return FileOut(id=f.id, filename=f.filename, mime_type=f.mime_type, created_at=str(f.created_at))

@router.get("", response_model=FileListOut)
async def list_files(
    session: AsyncSession = Depends(get_session),
    limit: int = 20,
    offset: int = 0,
):
    total = await session.scalar(select(func.count()).select_from(File))
    q = select(File).order_by(desc(File.created_at)).limit(limit).offset(offset)
    rows = (await session.execute(q)).scalars().all()
    items = [FileOut(id=f.id, filename=f.filename, mime_type=f.mime_type, created_at=str(f.created_at)) for f in rows]
    return FileListOut(items=items, total=int(total or 0))