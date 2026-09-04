"""Contrato estable entre el RAG y cualquier servicio de inferencia."""

from typing import Protocol


class InferenceError(Exception):
    """Error base comunicable por cualquier proveedor de inferencia."""


class InferenceUnavailableError(InferenceError):
    """El servicio de inferencia no está disponible o respondió incorrectamente."""


class InferenceModelNotFoundError(InferenceError):
    """El modelo configurado no está disponible en el proveedor."""


class InferenceClient(Protocol):
    """Operaciones requeridas sin depender del proveedor concreto."""

    async def generate(self, prompt: str, system: str | None = None) -> str: ...

    async def embed(self, text: str) -> list[float]: ...

    async def readiness(self) -> dict[str, str]: ...

    async def close(self) -> None: ...
