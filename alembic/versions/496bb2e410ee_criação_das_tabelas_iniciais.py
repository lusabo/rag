"""Criação das tabelas iniciais

Revision ID: 496bb2e410ee
Revises: 
Create Date: 2025-08-01 16:02:12.475490

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '496bb2e410ee'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Criação da tabela files
    op.execute("""
        CREATE TABLE files (
            id SERIAL PRIMARY KEY,
            filename TEXT NOT NULL,
            mime_type TEXT DEFAULT 'application/pdf',
            created_at TIMESTAMP DEFAULT NOW(),
            content BYTEA NOT NULL
        );
    """)

    # Criação da tabela chunks
    op.execute("""
        CREATE TABLE chunks (
            id SERIAL PRIMARY KEY,
            file_id INT NOT NULL REFERENCES files(id) ON DELETE CASCADE,
            page_number INT NOT NULL,
            chunk_index INT NOT NULL,
            text_cleaned TEXT NOT NULL,
            embedding VECTOR(1536),
            token_count INT
        );
    """)

    # Criação do índice vetorial
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_chunks_emb_hnsw
        ON chunks USING hnsw (embedding vector_l2_ops);
    """)

def downgrade():
    # Reverte as alterações
    op.execute("DROP INDEX IF EXISTS idx_chunks_emb_hnsw;")
    op.execute("DROP TABLE IF EXISTS chunks;")
    op.execute("DROP TABLE IF EXISTS files;")
