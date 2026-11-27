
import asyncio
import json
import logging
import sqlite3
import time

from datetime import datetime, timezone
from pathlib import Path

import httpx


logger = logging.getLogger(__name__)


class WeatherUnavailable(RuntimeError):
    pass


class OpenMeteoWeatherService:

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    CURRENT = (
        "temperature_2m,relative_humidity_2m,"
        "weather_code,wind_speed_10m"
    )

    HOURLY = "temperature_2m,precipitation_probability"

    DAILY = (
        "weather_code,temperature_2m_max,"
        "temperature_2m_min,precipitation_probability_max"
    )

    WEATHER_CODES = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snowfall",
        73: "Moderate snowfall",
        75: "Heavy snowfall",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }

    def __init__(
        self,
        latitude: float,
        longitude: float,
        timezone_name: str = "Asia/Kolkata",
        database_path: str = "data/weather.sqlite3",
        cache_ttl_seconds: int = 1800,
        stale_if_error_seconds: int = 21600,
        max_requests_per_day: int = 100,
    ):
        if not -90 <= latitude <= 90:
            raise ValueError("Invalid latitude.")

        if not -180 <= longitude <= 180:
            raise ValueError("Invalid longitude.")

        if cache_ttl_seconds <= 0:
            raise ValueError("Cache TTL must be positive.")

        if stale_if_error_seconds < cache_ttl_seconds:
            raise ValueError("Stale threshold must be at least the cache TTL.")

        if max_requests_per_day <= 0:
            raise ValueError("Daily request limit must be positive.")

        self.latitude = latitude
        self.longitude = longitude
        self.timezone_name = timezone_name

        self.cache_ttl = cache_ttl_seconds
        self.stale_ttl = stale_if_error_seconds
        self.daily_limit = max_requests_per_day

        db_path = Path(database_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self.db = sqlite3.connect(str(db_path))
        self.db.execute("PRAGMA journal_mode=WAL")

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS weather_cache (
                cache_key TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                fetched_at REAL NOT NULL
            )
        """)

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS weather_api_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_utc TEXT NOT NULL,
                attempted_at TEXT NOT NULL,
                success INTEGER NOT NULL DEFAULT 0,
                status_code INTEGER,
                duration_ms REAL
            )
        """)

        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_weather_usage_date
            ON weather_api_requests(date_utc)
        """)

        self.db.commit()

        self.cache_key = (
            f"{latitude}:{longitude}:{timezone_name}"
        )

        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0),
            headers={"User-Agent": "RoomOS/0.1"},
        )

        # Prevent concurrent requests from bypassing the cache.
        self._request_lock = asyncio.Lock()

    def _get_cache(self):
        row = self.db.execute(
            """
            SELECT payload, fetched_at
            FROM weather_cache
            WHERE cache_key = ?
            """,
            (self.cache_key,),
        ).fetchone()

        if row is None:
            return None

        return json.loads(row[0]), row[1]

    def _save_cache(self, payload: dict, fetched_at: float):
        self.db.execute(
            """
            INSERT OR REPLACE INTO weather_cache
            (cache_key, payload, fetched_at)
            VALUES (?, ?, ?)
            """,
            (
                self.cache_key,
                json.dumps(payload),
                fetched_at,
            ),
        )
        self.db.commit()

    def _usage_count_today(self) -> int:
        today = datetime.now(timezone.utc).date().isoformat()

        return self.db.execute(
            """
            SELECT COUNT(*)
            FROM weather_api_requests
            WHERE date_utc = ?
            """,
            (today,),
        ).fetchone()[0]

    def _record_attempt(self) -> int:
        now = datetime.now(timezone.utc)

        cursor = self.db.execute(
            """
            INSERT INTO weather_api_requests
            (date_utc, attempted_at)
            VALUES (?, ?)
            """,
            (now.date().isoformat(), now.isoformat()),
        )

        self.db.commit()
        return cursor.lastrowid

    def _finish_attempt(
        self,
        request_id: int,
        success: bool,
        status_code: int | None,
        duration_ms: float,
    ):
        self.db.execute(
            """
            UPDATE weather_api_requests
            SET success = ?, status_code = ?, duration_ms = ?
            WHERE id = ?
            """,
            (
                int(success),
                status_code,
                duration_ms,
                request_id,
            ),
        )
        self.db.commit()

    @classmethod
    def _condition(cls, code):
        return cls.WEATHER_CODES.get(
            code,
            f"Weather condition code {code}",
        )

    def _normalize(self, raw: dict) -> dict:
        current = raw["current"]
        hourly = raw["hourly"]
        daily = raw["daily"]

        current_time = current["time"]

        # Include the current hour and next 11 hourly entries.
        start_index = next(
            (
                i for i, timestamp in enumerate(hourly["time"])
                if timestamp >= current_time[:13]
            ),
            0,
        )

        hourly_forecast = []

        for i in range(start_index, min(start_index + 12, len(hourly["time"]))):
            hourly_forecast.append({
                "time": hourly["time"][i],
                "temperature_c": hourly["temperature_2m"][i],
                "precipitation_probability_percent":
                    hourly["precipitation_probability"][i],
            })

        daily_forecast = []

        for i, date in enumerate(daily["time"]):
            code = daily["weather_code"][i]

            daily_forecast.append({
                "date": date,
                "condition": self._condition(code),
                "temperature_max_c": daily["temperature_2m_max"][i],
                "temperature_min_c": daily["temperature_2m_min"][i],
                "precipitation_probability_percent":
                    daily["precipitation_probability_max"][i],
            })

        code = current["weather_code"]

        return {
            "location": {
                "latitude": raw["latitude"],
                "longitude": raw["longitude"],
                "timezone": raw["timezone"],
            },
            "current": {
                "time": current_time,
                "temperature_c": current["temperature_2m"],
                "humidity_percent": current["relative_humidity_2m"],
                "wind_speed_kmh": current["wind_speed_10m"],
                "condition": self._condition(code),
            },
            "hourly": hourly_forecast,
            "daily": daily_forecast,
            "attribution": {
                "text": "Weather data by Open-Meteo.com",
                "url": "https://open-meteo.com/",
            },
        }

    def _with_metadata(
        self,
        payload: dict,
        fetched_at: float,
        cache_hit: bool,
        stale: bool,
    ):
        result = dict(payload)

        result["metadata"] = {
            "fetched_at_utc": datetime.fromtimestamp(
                fetched_at, tz=timezone.utc
            ).isoformat(),
            "cache_hit": cache_hit,
            "stale": stale,
            "cache_age_seconds": max(
                0, int(time.time() - fetched_at)
            ),
        }

        return result

    async def get_forecast(self) -> dict:
        async with self._request_lock:
            cached = self._get_cache()
            now = time.time()

            if cached:
                payload, fetched_at = cached
                age = now - fetched_at

                if age < self.cache_ttl:
                    return self._with_metadata(
                        payload, fetched_at, True, False
                    )

            # Enforce our own conservative daily limit.
            if self._usage_count_today() >= self.daily_limit:
                if cached and age < self.stale_ttl:
                    logger.warning("Weather API budget exhausted; serving stale cache.")
                    return self._with_metadata(
                        payload, fetched_at, True, True
                    )

                raise WeatherUnavailable(
                    "RoomOS weather API request budget reached."
                )

            request_id = self._record_attempt()
            started = time.monotonic()
            status_code = None

            params = {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "current": self.CURRENT,
                "hourly": self.HOURLY,
                "daily": self.DAILY,
                "forecast_days": 3,
                "timezone": self.timezone_name,
                "temperature_unit": "celsius",
                "wind_speed_unit": "kmh",
            }

            try:
                response = await self.client.get(
                    self.BASE_URL,
                    params=params,
                )

                status_code = response.status_code
                response.raise_for_status()

                normalized = self._normalize(response.json())

                fetched_at = time.time()
                self._save_cache(normalized, fetched_at)

                self._finish_attempt(
                    request_id,
                    True,
                    status_code,
                    (time.monotonic() - started) * 1000,
                )

                logger.info(
                    "Open-Meteo request successful. Daily requests: %s/%s",
                    self._usage_count_today(),
                    self.daily_limit,
                )

                return self._with_metadata(
                    normalized, fetched_at, False, False
                )

            except Exception as exc:
                if isinstance(exc, httpx.HTTPStatusError):
                    status_code = exc.response.status_code

                self._finish_attempt(
                    request_id,
                    False,
                    status_code,
                    (time.monotonic() - started) * 1000,
                )

                logger.exception("Open-Meteo request failed.")

                if cached and (time.time() - fetched_at) < self.stale_ttl:
                    logger.warning("Serving stale weather cache.")
                    return self._with_metadata(
                        payload, fetched_at, True, True
                    )

                raise WeatherUnavailable(
                    "Weather data is currently unavailable."
                ) from exc

    def get_usage(self) -> dict:
        today = datetime.now(timezone.utc).date().isoformat()

        total, successful, failed, last_request = self.db.execute(
            """
            SELECT
                COUNT(*),
                COALESCE(SUM(success), 0),
                COALESCE(SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END), 0),
                MAX(attempted_at)
            FROM weather_api_requests
            WHERE date_utc = ?
            """,
            (today,),
        ).fetchone()

        return {
            "date_utc": today,
            "requests_attempted": total,
            "successful_requests": successful,
            "failed_requests": failed,
            "daily_application_limit": self.daily_limit,
            "requests_remaining": max(0, self.daily_limit - total),
            "last_request_at": last_request,
        }

    async def close(self):
        await self.client.aclose()
        self.db.close()
