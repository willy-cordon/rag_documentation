# Qdrant es la base vectorial donde se almacenan embeddings y metadatos.
import logging

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import ResponseHandlingException, UnexpectedResponse

from app.config import QDRANT_EFFECTIVE_COLLECTION, QDRANT_URL

logger = logging.getLogger(__name__)


class VectorStoreUnavailableError(Exception):
    """Qdrant no está disponible o rechazó una operación."""


class QdrantService:
    """Pequeña fachada para las operaciones de la colección RAG."""

    def __init__(self) -> None:
        # La URL se obtiene de variables de entorno para funcionar con Docker.
        self.client = QdrantClient(url=QDRANT_URL)

    def ensure_collection(self, dimension: int) -> None:
        """Crea la colección si falta o valida su dimensión existente."""
        try:
            collections = self.client.get_collections().collections
        except (ResponseHandlingException, UnexpectedResponse, OSError) as exc:
            raise VectorStoreUnavailableError("No se pudo consultar Qdrant.") from exc
        existing = next(
            (item for item in collections if item.name == QDRANT_EFFECTIVE_COLLECTION),
            None,
        )
        if existing is None:
            # La dimensión debe coincidir con la producida por el modelo de embeddings.
            try:
                self.client.create_collection(
                    collection_name=QDRANT_EFFECTIVE_COLLECTION,
                    vectors_config=models.VectorParams(
                        size=dimension, distance=models.Distance.COSINE
                    ),
                )
            except (ResponseHandlingException, UnexpectedResponse, OSError) as exc:
                raise VectorStoreUnavailableError(
                    "No se pudo crear la colección vectorial en Qdrant."
                ) from exc
            logger.info(
                "Qdrant collection created: collection=%s dimension=%d",
                QDRANT_EFFECTIVE_COLLECTION,
                dimension,
            )
            return
        try:
            info = self.client.get_collection(QDRANT_EFFECTIVE_COLLECTION)
        except (ResponseHandlingException, UnexpectedResponse, OSError) as exc:
            raise VectorStoreUnavailableError(
                "No se pudo inspeccionar la colección vectorial."
            ) from exc
        current_dimension = info.config.params.vectors.size
        if current_dimension != dimension:
            raise ValueError(
                f"La colección {QDRANT_EFFECTIVE_COLLECTION} tiene dimensión {current_dimension}, "
                f"pero el modelo devuelve dimensión {dimension}."
            )

    def replace_document(
        self, document_name: str, points: list[models.PointStruct], dimension: int
    ) -> None:
        """Reemplaza todos los puntos de un documento de forma idempotente."""
        self.ensure_collection(dimension)
        # Borrar primero evita duplicados al indexar nuevamente el mismo documento.
        try:
            self.client.delete(
                collection_name=QDRANT_EFFECTIVE_COLLECTION,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="document",
                                match=models.MatchValue(value=document_name),
                            )
                        ]
                    )
                ),
                wait=True,
            )
            self.client.upsert(
                collection_name=QDRANT_EFFECTIVE_COLLECTION, points=points, wait=True
            )
        except (ResponseHandlingException, UnexpectedResponse, OSError) as exc:
            raise VectorStoreUnavailableError(
                "No se pudo reemplazar el documento en Qdrant."
            ) from exc

    def search(self, vector: list[float], limit: int) -> list[models.ScoredPoint]:
        """Busca los fragmentos más parecidos al vector de consulta."""
        try:
            return self.client.query_points(
                collection_name=QDRANT_EFFECTIVE_COLLECTION,
                query=vector,
                limit=limit,
                with_payload=True,
            ).points
        except (ResponseHandlingException, UnexpectedResponse, OSError) as exc:
            raise VectorStoreUnavailableError(
                "No se pudo buscar en la colección vectorial. "
                "Indexá el documento para la configuración de embeddings activa."
            ) from exc

    def collection_exists(self) -> bool:
        """Indica si la colección configurada existe en Qdrant."""
        try:
            return any(
                item.name == QDRANT_EFFECTIVE_COLLECTION
                for item in self.client.get_collections().collections
            )
        except (ResponseHandlingException, UnexpectedResponse, OSError) as exc:
            raise VectorStoreUnavailableError("No se pudo consultar Qdrant.") from exc

    def readiness(self) -> dict[str, str]:
        """Comprueba conectividad y reporta la colección vectorial activa."""
        try:
            self.client.get_collections()
        except (ResponseHandlingException, UnexpectedResponse, OSError) as exc:
            raise VectorStoreUnavailableError(
                f"Qdrant no está listo en {QDRANT_URL}."
            ) from exc
        return {
            "status": "ready",
            "collection": QDRANT_EFFECTIVE_COLLECTION,
        }

    def close(self) -> None:
        self.client.close()


qdrant_service = QdrantService()
