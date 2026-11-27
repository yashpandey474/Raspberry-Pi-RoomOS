from pi_controller.voice.speech_formatter import SpeechTextFormatter


formatter = SpeechTextFormatter()

sample = """
## Weather Update

**Current temperature:** 27°C

- Condition: Partly cloudy
- Humidity: 65%
- Wind speed: 12 km/h

Tomorrow: Expect rain.
"""

print(formatter.format(sample))