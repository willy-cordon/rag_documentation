# Se configura un formato uniforme para observar las llamadas a los servicios.
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s"
)

from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.services.inference import InferenceError
from app.services.inference_service import close_inference_client, inference_readiness
from app.services.qdrant_service import VectorStoreUnavailableError, qdrant_service


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Libera conexiones persistentes durante el apagado de la API."""
    yield
    await close_inference_client()
    await asyncio.to_thread(qdrant_service.close)


# La instancia central de FastAPI registra metadatos visibles en Swagger.
app = FastAPI(
    title="Parking Meter AI MVP",
    description="Demo RAG desacoplada del proveedor de inferencia.",
    version="0.2.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    """Endpoint liviano para comprobar que la API está levantada."""
    return {"status": "ok"}


@app.get("/ready", tags=["system"])
async def ready() -> dict[str, object]:
    """Comprueba las dependencias necesarias para atender tráfico RAG."""
    try:
        inference = await inference_readiness()
        vector_store = await asyncio.to_thread(qdrant_service.readiness)
    except (InferenceError, VectorStoreUnavailableError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {
        "status": "ready",
        "dependencies": {
            "inference": inference,
            "vector_store": vector_store,
        },
    }


# Se registran por separado las rutas de chat simple y de RAG.
app.include_router(chat_router)
app.include_router(documents_router)
