# Qdrant es la base vectorial donde se almacenan embeddings y metadatos.
import logging
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.config import QDRANT_COLLECTION, QDRANT_URL

logger = logging.getLogger(__name__)


class QdrantService:
    """Pequeña fachada para las operaciones de la colección RAG."""

    def __init__(self) -> None:
        # La URL se obtiene de variables de entorno para funcionar con Docker.
        self.client = QdrantClient(url=QDRANT_URL)

    def ensure_collection(self, dimension: int) -> None:
        """Crea la colección si falta o valida su dimensión existente."""
        collections = self.client.get_collections().collections
        existing = next((item for item in collections if item.name == QDRANT_COLLECTION), None)
        if existing is None:
            # La dimensión debe coincidir con la producida por el modelo de embeddings.
            self.client.create_collection(
                collection_name=QDRANT_COLLECTION,
                vectors_config=models.VectorParams(size=dimension, distance=models.Distance.COSINE),
            )
            logger.info("Qdrant collection created: collection=%s dimension=%d", QDRANT_COLLECTION, dimension)
            return
        info = self.client.get_collection(QDRANT_COLLECTION)
        current_dimension = info.config.params.vectors.size
        if current_dimension != dimension:
            raise ValueError(
                f"La colección {QDRANT_COLLECTION} tiene dimensión {current_dimension}, "
                f"pero el modelo devuelve dimensión {dimension}."
            )

    def replace_document(self, document_name: str, points: list[models.PointStruct], dimension: int) -> None:
        """Reemplaza todos los puntos de un documento de forma idempotente."""
        self.ensure_collection(dimension)
        # Borrar primero evita duplicados al indexar nuevamente el mismo documento.
        self.client.delete(
            collection_name=QDRANT_COLLECTION,
            points_selector=models.FilterSelector(
                filter=models.Filter(must=[
                    models.FieldCondition(key="document", match=models.MatchValue(value=document_name))
                ])
            ),
            wait=True,
        )
        self.client.upsert(collection_name=QDRANT_COLLECTION, points=points, wait=True)

    def search(self, vector: list[float], limit: int) -> list[models.ScoredPoint]:
        """Busca los fragmentos más parecidos al vector de consulta."""
        return self.client.query_points(
            collection_name=QDRANT_COLLECTION,
            query=vector,
            limit=limit,
            with_payload=True,
        ).points

    def collection_exists(self) -> bool:
        """Indica si la colección configurada existe en Qdrant."""
        return any(item.name == QDRANT_COLLECTION for item in self.client.get_collections().collections)


qdrant_service = QdrantService()
