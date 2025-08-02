import httpx
from typing import List
from app.core.config import settings

class Embedder:
    async def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

class OpenAIEmbedder(Embedder):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    async def embed(self, texts: List[str]) -> List[List[float]]:
        url = "https://api.openai.com/v1/embeddings"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(url, headers=headers, json={"model": self.model, "input": texts})
            r.raise_for_status()
            data = r.json()
        return [d["embedding"] for d in data["data"]]

def get_embedder() -> Embedder:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY não configurada")
    return OpenAIEmbedder(settings.openai_api_key, settings.openai_embedding_model)