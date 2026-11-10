import httpx

from shared.contracts import ChatMessage


class OllamaProvider:
    def __init__(
        self,
        model: str,
        base_url: str = "http://127.0.0.1:11434"
    ):
        self.model = model
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=90.0
        )

    async def chat(self, messages: list[ChatMessage]) -> str:
        response = await self._client.post(
            "/api/chat", # posts to ollama api running on laptop
            json={
                "model": self.model,
                "messages": [
                    message.model_dump(mode="json", include={"role", "content"})
                    for message in messages
                ],
                "stream": False
            }
        )

        response.raise_for_status()
        return response.json()["message"]["content"]

    async def close(self):
        await self._client.aclose()