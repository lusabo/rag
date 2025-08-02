from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, Text, LargeBinary, ForeignKey, text as sqltext, TIMESTAMP
from pgvector.sqlalchemy import Vector

class Base(DeclarativeBase):
    pass

class File(Base):
    __tablename__ = "files"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(Text, nullable=False)
    mime_type: Mapped[str] = mapped_column(Text, nullable=False, server_default="application/pdf")
    created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=sqltext("NOW()"))
    content: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    chunks: Mapped[list["Chunk"]] = relationship(back_populates="file", cascade="all, delete-orphan")

class Chunk(Base):
    __tablename__ = "chunks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("files.id", ondelete="CASCADE"), index=True)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text_cleaned: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536))
    token_count: Mapped[int | None] = mapped_column(Integer)

    file = relationship("File", back_populates="chunks")