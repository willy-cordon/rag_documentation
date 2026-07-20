# Se configura un formato uniforme para observar las llamadas a los servicios.
import logging

from fastapi import FastAPI

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

from app.api.chat import router as chat_router
from app.api.documents import router as documents_router

# La instancia central de FastAPI registra metadatos visibles en Swagger.
app = FastAPI(
    title="Parking Meter AI MVP",
    description="Etapa 1: API de chat conectada a Ollama local.",
    version="0.1.0",
)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    """Endpoint liviano para comprobar que la API está levantada."""
    return {"status": "ok"}


# Se registran por separado las rutas de chat simple y de RAG.
app.include_router(chat_router)
app.include_router(documents_router)
