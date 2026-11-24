import asyncio
import platform
import psutil
import time


class SystemHealthTool:
    name = "get_system_health"
    description = (
        "Get CPU usage, memory usage, disk usage and uptime "
        "of the device running RoomOS."
    )

    parameters = {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    }

    def __init__(self, disk_path: str = "/"):
        self.disk_path = disk_path

    async def execute(self, arguments: dict) -> dict:
        return await asyncio.to_thread(self._collect)

    def _collect(self) -> dict:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(self.disk_path)

        result = {
            "hostname": platform.node(),
            "platform": platform.platform(),
            "architecture": platform.machine(),
            "cpu_cores": psutil.cpu_count(),
            "cpu_usage_percent": psutil.cpu_percent(interval=0.1),
            "memory": {
                "total_mb": round(memory.total / (1024 ** 2)),
                "available_mb": round(memory.available / (1024 ** 2)),
                "usage_percent": memory.percent,
            },
            "disk": {
                "path": self.disk_path,
                "total_gb": round(disk.total / (1024 ** 3), 2),
                "free_gb": round(disk.free / (1024 ** 3), 2),
                "usage_percent": disk.percent,
            },
            "uptime_seconds": round(time.time() - psutil.boot_time()),
        }

        return result