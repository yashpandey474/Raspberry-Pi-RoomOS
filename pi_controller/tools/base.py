from typing import Protocol, Any


class Tool(Protocol):
    name: str
    description: str
    parameters: dict[str, Any]

    async def execute(
        self,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        ...