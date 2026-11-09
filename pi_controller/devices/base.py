from typing import Protocol, Any


class Device(Protocol):
    id: str
    name: str
    device_type: str
    capabilities: tuple[str, ...]

    async def get_state(self) -> dict[str, Any]:
        ...

    async def execute(
        self,
        command: str,
        parameters: dict[str, Any]
    ) -> dict[str, Any]:
        ...