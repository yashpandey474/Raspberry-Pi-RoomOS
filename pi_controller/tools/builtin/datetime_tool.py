from datetime import datetime
from zoneinfo import ZoneInfo


class DateTimeTool:
    name = "get_datetime"
    description = "Get the current date, time and day of the week."

    parameters = {
        "type": "object",
        "properties": {
            "timezone": {
                "type": "string",
                "description": "Optional IANA timezone, e.g. Asia/Kolkata.",
            }
        },
        "required": [],
        "additionalProperties": False,
    }

    def __init__(self, default_timezone: str = "Asia/Kolkata"):
        self.default_timezone = default_timezone

    async def execute(self, arguments: dict | None = None) -> dict:
        timezone = arguments.get("timezone", self.default_timezone) if arguments is not None else self.default_timezone

        try:
            now = datetime.now(ZoneInfo(timezone))
        except Exception as exc:
            raise ValueError(f"Invalid timezone: {timezone}") from exc

        return {
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "day": now.strftime("%A"),
            "timezone": timezone,
            "iso_timestamp": now.isoformat(),
        }