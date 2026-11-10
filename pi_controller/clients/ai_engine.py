import httpx

from shared.contracts import AIEngineChatRequest, ChatResponse, HealthResponse
from shared.exceptions import AIEngineUnavailable
from pydantic import ValidationError

class AIEngineClient:

    def __init__(
        self,
        base_url: str,
        timeout_seconds: float = 3.0
    ):
        """We want one reusable HTTP client per service client instance, rather than creating a new connection pool for every request."""
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=httpx.Timeout(timeout_seconds)
        )

    async def health(self) -> HealthResponse:
        try:
            response = await self._client.get("/health")
            response.raise_for_status()
            return HealthResponse.model_validate(response.json())
        except httpx.TimeoutException as e:
            raise AIEngineUnavailable(f"AI engine is unavailable (timeout): {e}")
        except httpx.RequestError as e:
            raise AIEngineUnavailable(f"AI engine is unavailable (request error): {e}")
        except httpx.HTTPStatusError as e:
            raise AIEngineUnavailable(
                f"AI Engine returned {e.response.status_code}: "
                f"{e.response.text}"
            ) from e
        except Exception as e:
            raise AIEngineUnavailable(f"AI engine is unavailable (unexpected error): {e}")


    async def close(self):
        await self._client.aclose()

    async def chat(self, request: AIEngineChatRequest) -> ChatResponse:
        try:
            response = await self._client.post(
                "/v1/chat", # posts to the api running on laptop
                json=request.model_dump(mode="json"),
                timeout=httpx.Timeout(90.0, connect=3.0)
            )

            response.raise_for_status()

            return ChatResponse.model_validate(response.json())

        except (
            httpx.HTTPError,
            ValidationError,
            ValueError
        ) as e:
            raise AIEngineUnavailable(
                f"AI engine chat request failed: {e}"
            ) from e