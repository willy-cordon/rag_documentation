"""Fachada de inferencia usada por los casos de uso de la aplicación."""

from app.config import INFERENCE_PROVIDER
from app.services.inference import InferenceClient, InferenceError
from app.services.ollama_service import OllamaClient


def _build_client() -> InferenceClient:
    if INFERENCE_PROVIDER == "ollama":
        return OllamaClient()
    raise InferenceError(
        f"Proveedor de inferencia no soportado: {INFERENCE_PROVIDER!r}. "
        "Para esta demo usá 'ollama'."
    )


inference_client = _build_client()


async def generate_text(prompt: str, system: str | None = None) -> str:
    return await inference_client.generate(prompt, system)


async def generate_answer(question: str) -> str:
    return await generate_text(question)


async def generate_embedding(text: str) -> list[float]:
    return await inference_client.embed(text)


async def inference_readiness() -> dict[str, str]:
    return await inference_client.readiness()


async def close_inference_client() -> None:
    await inference_client.close()
