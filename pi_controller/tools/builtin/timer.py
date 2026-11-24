import asyncio
import logging
import time
import uuid

logger = logging.getLogger(__name__)


class TimerTool:
    name = "manage_timer"
    description = (
        "Start, list or cancel timers. "
        "Timers run independently of the current conversation."
    )

    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["start", "list", "cancel"],
            },
            "duration_seconds": {
                "type": "number",
                "description": "Duration for a new timer.",
                "minimum": 1,
                "maximum": 86400,
            },
            "timer_id": {
                "type": "string",
                "description": "ID of the timer to cancel.",
            },
            "label": {
                "type": "string",
                "description": "Optional timer description.",
            },
        },
        "required": ["action"],
        "additionalProperties": False,
    }

    def __init__(self):
        self._timers: dict[str, dict] = {}

    async def execute(self, arguments: dict) -> dict:
        action = arguments.get("action")

        if action == "start":
            return self._start(arguments)

        if action == "list":
            return self._list()

        if action == "cancel":
            return self._cancel(arguments.get("timer_id"))

        raise ValueError("Action must be start, list or cancel.")

    def _start(self, arguments: dict) -> dict:
        duration = arguments.get("duration_seconds")

        if isinstance(duration, bool) or not isinstance(duration, (int, float)):
            raise ValueError("Duration must be numeric.")

        if not 1 <= duration <= 86400:
            raise ValueError("Duration must be between 1 and 86400 seconds.")

        label = str(arguments.get("label", "Timer")).strip()[:80]
        timer_id = uuid.uuid4().hex[:12]

        task = asyncio.create_task(
            self._wait(timer_id, float(duration), label)
        )

        self._timers[timer_id] = {
            "label": label,
            "deadline": time.monotonic() + duration,
            "task": task,
        }

        return {
            "success": True,
            "timer_id": timer_id,
            "label": label,
            "duration_seconds": duration,
        }

    def _list(self) -> dict:
        active = [
            {
                "timer_id": timer_id,
                "label": entry["label"],
                "remaining_seconds": max(
                    0, round(entry["deadline"] - time.monotonic())
                ),
            }
            for timer_id, entry in self._timers.items()
        ]

        return {"active_timers": active}

    def _cancel(self, timer_id: str | None) -> dict:
        if not timer_id:
            raise ValueError("timer_id is required.")

        entry = self._timers.pop(timer_id, None)

        if not entry:
            return {"success": False, "message": "Timer not found."}

        entry["task"].cancel()

        return {
            "success": True,
            "message": f"Timer '{entry['label']}' cancelled.",
        }

    async def _wait(self, timer_id: str, duration: float, label: str):
        try:
            await asyncio.sleep(duration)
            self._timers.pop(timer_id, None)

            # Temporary notification mechanism.
            # We'll connect this to RoomOS voice notifications later.
            logger.info("TIMER EXPIRED: %s (ID: %s)", label, timer_id)

        except asyncio.CancelledError:
            raise

    async def close(self):
        tasks = [entry["task"] for entry in self._timers.values()]

        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)
        self._timers.clear()