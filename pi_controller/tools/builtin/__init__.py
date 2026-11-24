from pi_controller.tools.builtin.datetime_tool import DateTimeTool
from pi_controller.tools.builtin.calculator import CalculatorTool
from pi_controller.tools.builtin.unit_converter import UnitConverterTool
from pi_controller.tools.builtin.timer import TimerTool
from pi_controller.tools.builtin.system_health import SystemHealthTool


def register_builtin_tools(registry):
    timer_tool = TimerTool()

    tools = [
        DateTimeTool(),
        CalculatorTool(),
        UnitConverterTool(),
        timer_tool,
        SystemHealthTool(),
    ]

    for tool in tools:
        registry.register(tool)

    # we might need to close timer tool's outstanding tasks during application shutdown.
    return timer_tool