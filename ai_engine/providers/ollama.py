import httpx

from shared.contracts import AIEngineChatRequest, ChatMessage, ChatResponse


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

    async def chat(self, request: AIEngineChatRequest) -> ChatResponse:
        messages = [
            message.model_dump(mode="json", exclude_none=True)
            for message in request.messages
        ]

        tools = [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"],
                },
            }
            for tool in request.tools
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0,
                "num_ctx": self.context_length, # allocated context
                "num_predict": self.max_tokens # generated tokens
            },
        }

        if tools:
            payload["tools"] = tools

        response = await self._client.post(
                "/api/chat", # posts to ollama api running on laptop
                json=payload
            )

        response.raise_for_status()
        message = response.json()["message"]

        return ChatResponse(
            session_id=request.session_id,
            response=message.get("content") or "",
            thinking=message.get("thinking"),
            tool_calls=message.get("tool_calls") or []
        )

    async def close(self):
        await self._client.aclose()