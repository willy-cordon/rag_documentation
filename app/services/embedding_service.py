# Se reutiliza la integración centralizada con Ollama.
from app.services.ollama_service import generate_embedding


async def embed_text(text: str) -> list[float]:
    """Genera un vector semántico para un texto usando Ollama."""
    # Mantener esta función separada facilita cambiar el proveedor en el futuro.
    return await generate_embedding(text)
