# La configuración se toma del entorno para no acoplar el código a Docker o Windows.
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


# ``host.docker.internal`` permite que el contenedor alcance Ollama en Windows.
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
OLLAMA_TIMEOUT = _positive_float("OLLAMA_TIMEOUT", 120.0)
OLLAMA_NUM_PREDICT = _positive_int("OLLAMA_NUM_PREDICT", 512)
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333").rstrip("/")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "estacionamiento_documentation")
CHUNK_SIZE = _positive_int("CHUNK_SIZE", 1200)
CHUNK_OVERLAP = _positive_int("CHUNK_OVERLAP", 200)
RAG_TOP_K = _positive_int("RAG_TOP_K", 4)
