from pi_controller.tools.base import Tool
import logging
from jsonschema import validate

logger = logging.getLogger(__name__)

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        name = tool.name.strip()

        if not name:
            raise ValueError("Tool name cannot be empty.")

        if name in self._tools:
            raise ValueError(f"Tool already registered: {name}")

        self._tools[name] = tool

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")

        return self._tools[name]

    def list_tools(self) -> list[Tool]:
        return list(self._tools.values())

    def describe_tools(self) -> list[dict]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            }
            for tool in self._tools.values()
        ]



    async def execute(self, name: str, arguments: dict) -> dict:
        tool = self.get(name)

        if not isinstance(arguments, dict):
            raise ValueError("Tool arguments must be an object.")

        validate(
            instance=arguments,
            schema=tool.parameters,
        )

        result = await tool.execute(arguments)

        if not isinstance(result, dict):
            raise TypeError("Tool must return a dictionary.")

        logger.info(f"Successfully executed tool: {name}")
        return result