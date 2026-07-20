# Los modelos Pydantic validan automáticamente el JSON recibido por FastAPI.
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Cuerpo común de los endpoints que reciben una pregunta."""

    # Evita enviar preguntas vacías al modelo o al buscador vectorial.
    question: str = Field(..., min_length=1, description="Pregunta del usuario")
