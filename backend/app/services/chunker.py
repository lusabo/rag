from typing import List

def clean_text(s: str) -> str:
    return " ".join(s.split())

def chunk_text(text: str, max_chars: int = 1000, overlap: int = 150) -> List[str]:
    text = clean_text(text)
    chunks: List[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + max_chars, n)
        chunk = text[start:end]
        chunks.append(chunk)
        if end == n:
            break
        start = max(0, end - overlap)
    return chunks