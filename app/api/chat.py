# FastAPI se encarga de exponer el endpoint y traducir errores internos a HTTP.
from fastapi import APIRouter, HTTPException

from app.models.requests import ChatRequest
from app.models.responses import ChatResponse
from app.services.inference import (
    InferenceModelNotFoundError,
    InferenceUnavailableError,
)
from app.services.inference_service import generate_answer

# Este router agrupa los endpoints relacionados con el chat simple.
router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Genera una respuesta directa usando Ollama, sin recuperar documentos."""
    try:
        # El servicio encapsula la comunicación HTTP con el modelo local.
        answer = await generate_answer(request.question)
    except InferenceModelNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except InferenceUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    # Se devuelve siempre el mismo formato tipado para que Swagger lo documente.
    return ChatResponse(question=request.question, answer=answer)
