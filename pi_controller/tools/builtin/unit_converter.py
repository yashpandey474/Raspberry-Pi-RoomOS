import math


class UnitConverterTool:
    name = "convert_units"
    description = "Convert between supported units of length, mass, volume and temperature."

    parameters = {
        "type": "object",
        "properties": {
            "value": {
                "type": "number",
                "description": "Numeric value to convert.",
            },
            "from_unit": {"type": "string"},
            "to_unit": {"type": "string"},
        },
        "required": ["value", "from_unit", "to_unit"],
        "additionalProperties": False,
    }

    UNITS = {
        # Length: base unit = metre
        "m": ("length", 1),
        "meter": ("length", 1),
        "meters": ("length", 1),
        "km": ("length", 1000),
        "kilometer": ("length", 1000),
        "kilometers": ("length", 1000),
        "cm": ("length", 0.01),
        "mm": ("length", 0.001),
        "mile": ("length", 1609.344),
        "miles": ("length", 1609.344),
        "ft": ("length", 0.3048),
        "feet": ("length", 0.3048),
        "in": ("length", 0.0254),
        "inch": ("length", 0.0254),
        "inches": ("length", 0.0254),

        # Mass: base unit = kilogram
        "kg": ("mass", 1),
        "kilogram": ("mass", 1),
        "kilograms": ("mass", 1),
        "g": ("mass", 0.001),
        "gram": ("mass", 0.001),
        "grams": ("mass", 0.001),
        "lb": ("mass", 0.45359237),
        "lbs": ("mass", 0.45359237),
        "pound": ("mass", 0.45359237),
        "oz": ("mass", 0.028349523125),
        "ounce": ("mass", 0.028349523125),

        # Volume: base unit = litre
        "l": ("volume", 1),
        "liter": ("volume", 1),
        "litre": ("volume", 1),
        "ml": ("volume", 0.001),
        "milliliter": ("volume", 0.001),
        "gallon": ("volume", 3.785411784),
        "gallons": ("volume", 3.785411784),
    }

    TEMPERATURE_UNITS = {
        "c", "celsius", "°c",
        "f", "fahrenheit", "°f",
        "k", "kelvin",
    }

    @staticmethod
    def _to_kelvin(value: float, unit: str) -> float:
        if unit in ("c", "celsius", "°c"):
            result = value + 273.15
        elif unit in ("f", "fahrenheit", "°f"):
            result = (value - 32) * 5 / 9 + 273.15
        else:
            result = value

        if result < 0:
            raise ValueError("Temperature cannot be below absolute zero.")

        return result

    @staticmethod
    def _from_kelvin(value: float, unit: str) -> float:
        if unit in ("c", "celsius", "°c"):
            return value - 273.15
        if unit in ("f", "fahrenheit", "°f"):
            return (value - 273.15) * 9 / 5 + 32
        return value

    async def execute(self, arguments: dict) -> dict:
        value = arguments.get("value")
        source = str(arguments.get("from_unit", "")).strip().lower()
        target = str(arguments.get("to_unit", "")).strip().lower()

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("Value must be numeric.")

        if not math.isfinite(value):
            raise ValueError("Value must be finite.")

        if source in self.TEMPERATURE_UNITS and target in self.TEMPERATURE_UNITS:
            result = self._from_kelvin(
                self._to_kelvin(value, source),
                target,
            )
        else:
            source_data = self.UNITS.get(source)
            target_data = self.UNITS.get(target)

            if not source_data or not target_data:
                raise ValueError("Unsupported unit.")

            if source_data[0] != target_data[0]:
                raise ValueError("Units belong to different dimensions.")

            base_value = value * source_data[1]
            result = base_value / target_data[1]

        return {
            "original_value": value,
            "from_unit": source,
            "to_unit": target,
            "converted_value": round(result, 8),
        }