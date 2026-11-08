import httpx

from shared.contracts import HealthResponse
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
            raise AIEngineUnavailable(f"AI engine is unavailable (HTTP error): {e}")
        except Exception as e:
            raise AIEngineUnavailable(f"AI engine is unavailable (unexpected error): {e}")


    async def close(self):
        await self._client.aclose()