# La configuración se toma del entorno para no acoplar el código a Docker o Windows.
import hashlib
import os


def _positive_float(name: str, default: float) -> float:
    """Lee un decimal positivo desde el entorno y falla con un mensaje claro."""
    value = os.getenv(name, str(default))
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError(f"{name} debe ser un número válido") from exc
    if parsed <= 0:
        raise ValueError(f"{name} debe ser mayor que cero")
    return parsed


def _positive_int(name: str, default: int) -> int:
    """Lee un entero positivo desde el entorno y falla con un mensaje claro."""
    value = os.getenv(name, str(default))
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"{name} debe ser un entero válido") from exc
    if parsed <= 0:
        raise ValueError(f"{name} debe ser mayor que cero")
    return parsed


# La aplicación depende de contratos de generación y embeddings, no del runtime
# concreto. En desarrollo ambos endpoints apuntan al contenedor de Ollama.
INFERENCE_PROVIDER = os.getenv("INFERENCE_PROVIDER", "ollama").strip().lower()
GENERATION_BASE_URL = os.getenv("GENERATION_BASE_URL", "http://ollama:11434").rstrip(
    "/"
)
GENERATION_MODEL = os.getenv("GENERATION_MODEL", "llama3.2:latest")
EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", "http://ollama:11434").rstrip("/")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
EMBEDDING_MODEL_REVISION = os.getenv("EMBEDDING_MODEL_REVISION", "v1")
INFERENCE_TIMEOUT = _positive_float("INFERENCE_TIMEOUT", 300.0)
INFERENCE_CONNECT_TIMEOUT = _positive_float("INFERENCE_CONNECT_TIMEOUT", 5.0)
INFERENCE_MAX_CONNECTIONS = _positive_int("INFERENCE_MAX_CONNECTIONS", 10)
GENERATION_MAX_TOKENS = _positive_int("GENERATION_MAX_TOKENS", 256)
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333").rstrip("/")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "estacionamiento_documentation")
CHUNK_SIZE = _positive_int("CHUNK_SIZE", 1200)
CHUNK_OVERLAP = _positive_int("CHUNK_OVERLAP", 200)
RAG_TOP_K = _positive_int("RAG_TOP_K", 3)

# Un cambio de proveedor, modelo o revisión crea otro espacio vectorial. Esto
# evita mezclar vectores compatibles en dimensión pero no en significado.
EMBEDDING_FINGERPRINT = (
    f"{INFERENCE_PROVIDER}:{EMBEDDING_MODEL}:{EMBEDDING_MODEL_REVISION}"
)
EMBEDDING_COLLECTION_SUFFIX = hashlib.sha256(
    EMBEDDING_FINGERPRINT.encode()
).hexdigest()[:10]
QDRANT_EFFECTIVE_COLLECTION = f"{QDRANT_COLLECTION}__{EMBEDDING_COLLECTION_SUFFIX}"
