# Esta fachada mantiene al RAG independiente del proveedor concreto.
from app.services.inference_service import generate_embedding


async def embed_text(text: str) -> list[float]:
    """Genera un vector semántico mediante el proveedor configurado."""
    return await generate_embedding(text)
