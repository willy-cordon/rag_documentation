# Cliente HTTP asíncrono para no bloquear el servidor mientras responde Ollama.
import httpx

from app.config import OLLAMA_EMBEDDING_MODEL, OLLAMA_MODEL, OLLAMA_NUM_PREDICT, OLLAMA_TIMEOUT, OLLAMA_URL


class OllamaUnavailableError(Exception):
    """Ollama cannot be reached or returned an invalid response."""


class OllamaModelNotFoundError(Exception):
    """The configured Ollama model is not installed."""


async def generate_answer(question: str) -> str:
    """Atajo para generar una respuesta sin contexto RAG."""
    return await generate_text(question)


async def generate_text(prompt: str, system: str | None = None) -> str:
    """Envía un prompt al endpoint de generación de Ollama y valida su respuesta."""
    # Desactivamos el razonamiento visible para devolver una respuesta limpia.
    prompt = f"/no_think\n{prompt}"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": OLLAMA_NUM_PREDICT},
        "think": False,
    }
    if system:
        payload["system"] = system
    try:
        # El cliente se crea por llamada para mantener el servicio simple y stateless.
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
            response = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
    except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as exc:
        raise OllamaUnavailableError(
            f"No se pudo conectar con Ollama en {OLLAMA_URL}. "
            "Verificá que Ollama esté ejecutándose y sea accesible desde Docker."
        ) from exc

    # Ollama usa 404 cuando el modelo configurado no está disponible.
    if response.status_code == 404:
        raise OllamaModelNotFoundError(
            f"El modelo Ollama '{OLLAMA_MODEL}' no existe o no está instalado. "
            "Revisá OLLAMA_MODEL y ejecutá 'ollama list'."
        )
    if response.is_error:
        detail = response.text[:500]
        raise OllamaUnavailableError(
            f"Ollama respondió con HTTP {response.status_code}: {detail}"
        )

    try:
        # La API devuelve el texto generado en la propiedad ``response``.
        data = response.json()
        answer = data["response"]
    except (ValueError, KeyError, TypeError) as exc:
        raise OllamaUnavailableError("Ollama devolvió una respuesta inválida.") from exc

    if not isinstance(answer, str):
        raise OllamaUnavailableError("Ollama devolvió un campo 'response' inválido.")
    answer = answer.strip()
    if "</think>" in answer:
        answer = answer.rsplit("</think>", 1)[1].strip()
    return answer


async def generate_embedding(text: str) -> list[float]:
    """Solicita a Ollama el embedding de un único texto."""
    payload = {"model": OLLAMA_EMBEDDING_MODEL, "input": text}
    try:
        # ``/api/embed`` devuelve una lista; este MVP usa el primer vector.
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
            response = await client.post(f"{OLLAMA_URL}/api/embed", json=payload)
    except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as exc:
        raise OllamaUnavailableError(
            f"No se pudo conectar con Ollama en {OLLAMA_URL} para generar embeddings."
        ) from exc

    if response.status_code == 404:
        raise OllamaModelNotFoundError(
            f"El modelo de embeddings '{OLLAMA_EMBEDDING_MODEL}' no existe o no está instalado. "
            "Instalalo con Ollama después de confirmar la descarga."
        )
    if response.is_error:
        raise OllamaUnavailableError(
            f"Ollama respondió con HTTP {response.status_code} al generar el embedding: "
            f"{response.text[:500]}"
        )

    try:
        embeddings = response.json()["embeddings"]
        vector = embeddings[0]
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise OllamaUnavailableError("Ollama devolvió un embedding inválido.") from exc
    if not isinstance(vector, list) or not vector:
        raise OllamaUnavailableError("Ollama devolvió un vector de embedding vacío.")
    return vector
