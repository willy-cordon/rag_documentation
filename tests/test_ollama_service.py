import unittest

import httpx

from app.services.inference import InferenceModelNotFoundError
from app.services.ollama_service import OllamaClient


class OllamaClientTest(unittest.IsolatedAsyncioTestCase):
    async def test_generate_and_embed_use_the_provider_contract(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/api/generate":
                return httpx.Response(200, json={"response": "respuesta"})
            if request.url.path == "/api/embed":
                return httpx.Response(200, json={"embeddings": [[0.1, 0.2, 0.3]]})
            return httpx.Response(404)

        client = OllamaClient(transport=httpx.MockTransport(handler))
        try:
            self.assertEqual(await client.generate("pregunta"), "respuesta")
            self.assertEqual(await client.embed("texto"), [0.1, 0.2, 0.3])
        finally:
            await client.close()

    async def test_readiness_validates_both_models(self) -> None:
        async def handler(_: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "models": [
                        {"model": "llama3.2:latest"},
                        {"name": "nomic-embed-text:latest"},
                    ]
                },
            )

        client = OllamaClient(transport=httpx.MockTransport(handler))
        try:
            self.assertEqual(
                await client.readiness(),
                {"generation": "ready", "embedding": "ready"},
            )
        finally:
            await client.close()

    async def test_readiness_fails_when_a_model_is_missing(self) -> None:
        async def handler(_: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"models": [{"model": "llama3.2:latest"}]})

        client = OllamaClient(transport=httpx.MockTransport(handler))
        try:
            with self.assertRaises(InferenceModelNotFoundError):
                await client.readiness()
        finally:
            await client.close()


if __name__ == "__main__":
    unittest.main()
