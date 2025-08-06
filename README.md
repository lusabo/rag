# 📄 RAG com PostgreSQL, pgvector e LLM

Este projeto implementa um sistema completo de **Retrieval-Augmented Generation (RAG)** com as seguintes tecnologias:

- **PostgreSQL** + `pgvector` como banco de vetores  
- **FastAPI** como backend para upload, ingestão e busca semântica  
- **LLM local** (ou via OpenAI) para geração de respostas  
- **Streamlit** como frontend interativo  
- **Docker** para facilitar o setup de ambiente

## 🚀 Funcionalidades

- Upload de arquivos PDF  
- Extração e chunking do conteúdo  
- Geração de embeddings com modelo open-source ou OpenAI  
- Armazenamento vetorial com pgvector  
- Busca semântica por similaridade vetorial  
- Geração de respostas com LLM  
- Interface web via Streamlit

## ⚙️ Requisitos

- [Docker](https://www.docker.com/)  
- [Python 3.12+](https://www.python.org/downloads/)  
- [uv](https://docs.astral.sh/uv/)

## 📦 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/lusabo/rag.git
cd rag
```

### 2. Configure o .env

```dotenv
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=rag
POSTGRES_DB_HOST=localhost
POSTGRES_DB_PORT=5432

# pgAdmin
PGADMIN_DEFAULT_EMAIL=admin@admin.com
PGADMIN_DEFAULT_PASSWORD=admin

# Embeddings (opcional)
OPENAI_API_KEY=sk-...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536
```

### 🐳 Subindo containers

```bash
cd docker
docker compose up -d
```

### 🧠 Inicialize o banco

```bash
cd ..
uv pip install .
alembic upgrade head
```
### 🖥️ Rode o backend

```bash
uv run python -m uvicorn --app-dir backend app.main:app --reload
```

### 🌐 Rode o frontend (Streamlit)

```bash
streamlit run frontend/app.py
```

•	Acesse: http://localhost:8501

### 🧪 Teste

1.	Faça upload de PDFs
2.	Consulte os documentos com perguntas em linguagem natural

### 📁 Estrutura

```bash
rag/
├── alembic/
├── backend/
├── docker/
├── frontend/
├── .env
├── alembic.ini
└── pyproject.toml
```
### 🤝 Contribua

Pull requests são bem-vindos! 🙌

### 💬 Contato

Fale comigo no [LinkedIn](https://www.linkedin.com/in/luciano-borges/)

⭐ Se curtiu, deixe uma estrela no repositório!
