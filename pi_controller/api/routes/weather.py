from fastapi import APIRouter, Request, HTTPException

from pi_controller.services.weather_service import (
    OpenMeteoWeatherService,
    WeatherUnavailable,
)

router = APIRouter(prefix="/weather", tags=["Weather"])


def get_service(request: Request) -> OpenMeteoWeatherService:
    return request.app.state.weather_service


@router.get("/forecast")
async def forecast(request: Request):
    try:
        return await get_service(request).get_forecast()
    except WeatherUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.get("/usage")
async def usage(request: Request):
    return get_service(request).get_usage()