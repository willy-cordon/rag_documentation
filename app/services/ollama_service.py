"""Adaptador de Ollama para el contrato genérico de inferencia."""

from collections.abc import Iterable

import httpx

from app.config import (
    EMBEDDING_BASE_URL,
    EMBEDDING_MODEL,
    GENERATION_BASE_URL,
    GENERATION_MAX_TOKENS,
    GENERATION_MODEL,
    INFERENCE_CONNECT_TIMEOUT,
    INFERENCE_MAX_CONNECTIONS,
    INFERENCE_TIMEOUT,
)
from app.services.inference import (
    InferenceModelNotFoundError,
    InferenceUnavailableError,
)


class OllamaClient:
    """Cliente reutilizable para generación y embeddings mediante Ollama."""

    def __init__(self, transport: httpx.AsyncBaseTransport | None = None) -> None:
        timeout = httpx.Timeout(
            connect=INFERENCE_CONNECT_TIMEOUT,
            read=INFERENCE_TIMEOUT,
            write=INFERENCE_TIMEOUT,
            pool=INFERENCE_CONNECT_TIMEOUT,
        )
        limits = httpx.Limits(
            max_connections=INFERENCE_MAX_CONNECTIONS,
            max_keepalive_connections=INFERENCE_MAX_CONNECTIONS,
        )
        selected_transport = transport or httpx.AsyncHTTPTransport(retries=1)
        self._client = httpx.AsyncClient(
            timeout=timeout,
            limits=limits,
            transport=selected_transport,
        )

    async def _post(
        self, url: str, payload: dict[str, object], operation: str
    ) -> httpx.Response:
        try:
            response = await self._client.post(url, json=payload)
        except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as exc:
            raise InferenceUnavailableError(
                f"No se pudo conectar con el servicio de inferencia durante {operation}."
            ) from exc
        if response.status_code == 404:
            model = payload.get("model", "desconocido")
            raise InferenceModelNotFoundError(
                f"El modelo de inferencia {model!r} no está disponible. "
                "Revisá el estado del servicio ollama-init."
            )
        if response.is_error:
            raise InferenceUnavailableError(
                f"El servicio de inferencia respondió HTTP {response.status_code} "
                f"durante {operation}: {response.text[:500]}"
            )
        return response

    async def generate(self, prompt: str, system: str | None = None) -> str:
        """Genera texto usando el modelo configurado."""
        payload: dict[str, object] = {
            "model": GENERATION_MODEL,
            "prompt": f"/no_think\n{prompt}",
            "stream": False,
            "options": {"num_predict": GENERATION_MAX_TOKENS},
            "think": False,
        }
        if system:
            payload["system"] = system
        response = await self._post(
            f"{GENERATION_BASE_URL}/api/generate", payload, "la generación"
        )
        try:
            answer = response.json()["response"]
        except (ValueError, KeyError, TypeError) as exc:
            raise InferenceUnavailableError(
                "El servicio de inferencia devolvió una respuesta de generación inválida."
            ) from exc
        if not isinstance(answer, str):
            raise InferenceUnavailableError(
                "El campo 'response' de inferencia es inválido."
            )
        answer = answer.strip()
        if "</think>" in answer:
            answer = answer.rsplit("</think>", 1)[1].strip()
        return answer

    async def embed(self, text: str) -> list[float]:
        """Genera el vector de un texto usando el modelo configurado."""
        payload: dict[str, object] = {"model": EMBEDDING_MODEL, "input": text}
        response = await self._post(
            f"{EMBEDDING_BASE_URL}/api/embed", payload, "la generación de embeddings"
        )
        try:
            vector = response.json()["embeddings"][0]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise InferenceUnavailableError(
                "El servicio de inferencia devolvió un embedding inválido."
            ) from exc
        if not isinstance(vector, list) or not vector:
            raise InferenceUnavailableError("El servicio devolvió un embedding vacío.")
        return vector

    @staticmethod
    def _has_model(models: Iterable[dict[str, object]], expected: str) -> bool:
        expected_with_tag = expected if ":" in expected else f"{expected}:latest"
        for model in models:
            actual = model.get("model") or model.get("name")
            if actual in {expected, expected_with_tag}:
                return True
        return False

    async def readiness(self) -> dict[str, str]:
        """Comprueba endpoints y presencia de modelos sin ejecutar inferencia."""
        endpoints = {
            "generation": (GENERATION_BASE_URL, GENERATION_MODEL),
            "embedding": (EMBEDDING_BASE_URL, EMBEDDING_MODEL),
        }
        result: dict[str, str] = {}
        cache: dict[str, list[dict[str, object]]] = {}
        for name, (base_url, model_name) in endpoints.items():
            if base_url not in cache:
                try:
                    response = await self._client.get(f"{base_url}/api/tags")
                    response.raise_for_status()
                    models = response.json()["models"]
                    if not isinstance(models, list):
                        raise TypeError
                    cache[base_url] = models
                except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
                    raise InferenceUnavailableError(
                        f"El endpoint de {name} no está listo en {base_url}."
                    ) from exc
            if not self._has_model(cache[base_url], model_name):
                raise InferenceModelNotFoundError(
                    f"El modelo {model_name!r} requerido para {name} no está disponible."
                )
            result[name] = "ready"
        return result

    async def close(self) -> None:
        await self._client.aclose()
