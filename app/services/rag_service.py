# asyncio.to_thread permite ejecutar el cliente síncrono de Qdrant sin bloquear FastAPI.
import asyncio
import logging
import time
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from qdrant_client.http import models

from app.config import EMBEDDING_FINGERPRINT, RAG_TOP_K
from app.models.responses import Source
from app.services.document_service import chunk_document, read_document
from app.services.embedding_service import embed_text
from app.services.inference_service import generate_text
from app.services.qdrant_service import qdrant_service

logger = logging.getLogger(__name__)

RAG_SYSTEM_PROMPT = (
    "Sos un asistente de soporte del sistema de Estacionamiento Medido.\n"
    "Respondé únicamente utilizando la información proporcionada en el contexto.\n"
    "No inventes procedimientos, opciones, configuraciones ni datos.\n"
    "Si la respuesta no está disponible en el contexto recuperado, indicá claramente "
    "que no disponés de información suficiente en la documentación.\n"
    "Respondé en español de forma clara y concisa."
)


async def index_document(document_name: str) -> tuple[int, int]:
    """Indexa un documento: lectura, chunking, embeddings y persistencia."""
    markdown = read_document(document_name)
    chunks = chunk_document(document_name, markdown)
    if not chunks:
        raise ValueError("El documento no produjo chunks")
    # Se genera un embedding por chunk para buscar luego por similitud semántica.
    vectors = [await embed_text(chunk.text) for chunk in chunks]
    dimension = len(vectors[0])
    # UUID5 garantiza el mismo ID cuando el mismo documento se indexa otra vez.
    points = [
        models.PointStruct(
            id=str(uuid5(NAMESPACE_URL, f"{chunk.document}:{chunk.chunk_id}")),
            vector=vector,
            payload={
                "text": chunk.text,
                "document": chunk.document,
                "section": chunk.section,
                "chunk_id": chunk.chunk_id,
                "title": chunk.title,
                "page": chunk.page,
                "embedding_fingerprint": EMBEDDING_FINGERPRINT,
            },
        )
        for chunk, vector in zip(chunks, vectors, strict=True)
    ]
    await asyncio.to_thread(
        qdrant_service.replace_document, document_name, points, dimension
    )
    logger.info(
        "Document indexed: document=%s chunks=%d dimension=%d",
        document_name,
        len(chunks),
        dimension,
    )
    return len(chunks), dimension


async def answer_question(question: str) -> tuple[str, list[Source]]:
    """Recupera contexto relevante y genera una respuesta fundamentada."""
    started = time.perf_counter()
    # La pregunta se transforma al mismo espacio vectorial que los documentos.
    query_vector = await embed_text(question)
    search_started = time.perf_counter()
    results = await asyncio.to_thread(qdrant_service.search, query_vector, RAG_TOP_K)
    search_ms = (time.perf_counter() - search_started) * 1000
    logger.info(
        "RAG search: question=%r chunks=%d search_ms=%.2f",
        question,
        len(results),
        search_ms,
    )
    if not results:
        return (
            "No encuentro información suficiente en la documentación disponible.",
            [],
        )

    context_parts: list[str] = []
    sources: list[Source] = []
    # Se construyen simultáneamente el prompt y las fuentes explicables de la API.
    for result in results:
        payload: dict[str, Any] = result.payload or {}
        score = float(result.score)
        document = str(payload.get("document", "desconocido"))
        section = str(payload.get("section", "desconocida"))
        chunk_id = str(payload.get("chunk_id", result.id))
        logger.info(
            "RAG result: score=%.4f document=%s section=%s", score, document, section
        )
        context_parts.append(
            f"[Documento: {document} | Sección: {section} | Chunk: {chunk_id}]\n{payload.get('text', '')}"
        )
        sources.append(
            Source(document=document, section=section, chunk_id=chunk_id, score=score)
        )

    # Los separadores ayudan al modelo a distinguir cada fragmento recuperado.
    context = "\n\n---\n\n".join(context_parts)
    prompt = f"/no_think\nCONTEXTO DOCUMENTAL:\n{context}\n\nPREGUNTA DEL USUARIO:\n{question}"
    llm_started = time.perf_counter()
    answer = await generate_text(prompt, system=RAG_SYSTEM_PROMPT)
    llm_ms = (time.perf_counter() - llm_started) * 1000
    total_ms = (time.perf_counter() - started) * 1000
    logger.info("RAG generation: llm_ms=%.2f total_ms=%.2f", llm_ms, total_ms)
    return answer, sources
