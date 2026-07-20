# Estos tipos definen el contrato de salida visible en Swagger y para los clientes.
from pydantic import BaseModel


class ChatResponse(BaseModel):
    """Respuesta del chat simple, sin fuentes documentales."""
    question: str
    answer: str


class Source(BaseModel):
    """Referencia al fragmento que aportó contexto a una respuesta RAG."""
    document: str
    section: str
    chunk_id: str
    score: float


class RagResponse(BaseModel):
    """Respuesta RAG junto con las fuentes recuperadas."""
    question: str
    answer: str
    sources: list[Source]


class IndexResponse(BaseModel):
    """Resumen de una operación de indexación."""
    status: str
    document: str
    chunks_created: int
    embedding_dimension: int
