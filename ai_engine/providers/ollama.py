import httpx

from shared.contracts import ChatMessage


class OllamaProvider:
    def __init__(
        self,
        model: str,
        base_url: str,
        request_timeout_seconds: float,
        connect_timeout_seconds: float,
        context_length: int,
        max_tokens: int
    ):
        self.model = model
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=httpx.Timeout(
                request_timeout_seconds,
                connect=connect_timeout_seconds
            )        
        )
        self.context_length = context_length
        self.max_tokens = max_tokens

    async def chat(self, messages: list[ChatMessage]) -> str:
        response = await self._client.post(
            "/api/chat", # posts to ollama api running on laptop
            json={
                "model": self.model,
                "messages": [
                    message.model_dump(mode="json", include={"role", "content"})
                    for message in messages
                ],
                "stream": False,
                "options": {
                    "num_ctx": self.context_length, # allocated context
                    "num_predict": self.max_tokens # generated tokens
                }
            }
        )

        response.raise_for_status()
        return response.json()["message"]["content"]

    async def close(self):
        await self._client.aclose()