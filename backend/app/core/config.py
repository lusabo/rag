from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Postgres (.env existente)
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "rag"
    POSTGRES_DB_HOST: str = "localhost"
    POSTGRES_DB_PORT: int = 5432

    # Embeddings
    embeddings_provider: str = "openai"
    openai_api_key: str | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536
    max_upload_mb: int = 25

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_DB_HOST}:{self.POSTGRES_DB_PORT}/{self.POSTGRES_DB}"
        )

settings = Settings()