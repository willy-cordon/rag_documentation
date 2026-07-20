# Logging permite diagnosticar fallos de indexación sin exponer el contenido completo.
import logging

from fastapi import APIRouter, HTTPException

from app.models.requests import ChatRequest
from app.models.responses import IndexResponse, RagResponse
from app.services.ollama_service import OllamaModelNotFoundError, OllamaUnavailableError
from app.services.rag_service import answer_question, index_document

logger = logging.getLogger(__name__)
router = APIRouter(tags=["rag"])
# Documento de ejemplo incluido en el repositorio y montado dentro del contenedor.
DOCUMENT_NAME = "manual_estacionamiento_medido.md"


@router.post("/documents/index", response_model=IndexResponse)
async def index_documents() -> IndexResponse:
    """Lee, divide, vectoriza y persiste el manual de documentación."""
    try:
        # La lógica pesada vive en el servicio RAG para mantener delgada la API.
        chunks_created, dimension = await index_document(DOCUMENT_NAME)
    except (FileNotFoundError, ValueError, OllamaModelNotFoundError, OllamaUnavailableError) as exc:
        logger.exception("Document indexing failed")
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return IndexResponse(
        status="indexed",
        document=DOCUMENT_NAME,
        chunks_created=chunks_created,
        embedding_dimension=dimension,
    )


@router.post("/rag/chat", response_model=RagResponse)
async def rag_chat(request: ChatRequest) -> RagResponse:
    """Responde una pregunta usando búsqueda semántica y contexto documental."""
    logger.info("RAG request received: question_length=%d", len(request.question))
    try:
        # Primero se recuperan los fragmentos relevantes y luego se consulta al LLM.
        answer, sources = await answer_question(request.question)
    except (ValueError, OllamaModelNotFoundError, OllamaUnavailableError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return RagResponse(question=request.question, answer=answer, sources=sources)
