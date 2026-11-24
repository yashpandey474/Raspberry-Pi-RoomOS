import asyncio

from pi_controller.tools.registry import ToolRegistry
from pi_controller.tools.builtin import register_builtin_tools


async def main():
    registry = ToolRegistry()
    timer_tool = register_builtin_tools(registry)

    print("Registered:", [tool.name for tool in registry.list_tools()])

    print("\nDate/time:")
    print(await registry.get("get_datetime").execute({}))

    print("\nCalculator:")
    print(await registry.get("calculate").execute({
        "expression": "12500 * 0.18"
    }))

    print("\nUnit converter:")
    print(await registry.get("convert_units").execute({
        "value": 5,
        "from_unit": "miles",
        "to_unit": "km",
    }))

    print("\nSystem health:")
    print(await registry.get("get_system_health").execute({}))

    print("\nTimer:")
    print(await registry.get("manage_timer").execute({
        "action": "start",
        "duration_seconds": 3,
        "label": "Test timer",
    }))

    await asyncio.sleep(4)
    await timer_tool.close()


if __name__ == "__main__":
    asyncio.run(main())