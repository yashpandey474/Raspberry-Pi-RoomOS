from pi_controller.services.weather_service import (
    OpenMeteoWeatherService,
)


class WeatherTool:
    name = "get_weather_forecast"

    description = (
        "Get current weather, the next 12 hours of hourly weather, "
        "and a 3-day daily forecast for the configured RoomOS location. "
        "Use daily[1] for tomorrow's forecast. "
        "The result includes temperature, rain probability, "
        "humidity, wind and weather conditions."
    )

    parameters = {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    }

    def __init__(self, weather_service: OpenMeteoWeatherService):
        self.weather_service = weather_service

    async def execute(self, arguments: dict) -> dict:
        if arguments:
            raise ValueError("This weather tool does not accept arguments.")

        return await self.weather_service.get_forecast()