"""
STT and microphone handling are separate responsibilities.

Vosk doesn't need to know where the audio came from, It just needs properly formatted audio frames.

- Sample rate: 16,000 Hz
- Channels: 1 (mono)
- Format: signed 16-bit PCM
=> One audio format across both machines.
"""
import json
import wave
from vosk import Model, KaldiRecognizer, SetLogLevel
import logging

logger = logging.getLogger(__name__)

class VoskSTT:
    def __init__(self, model_path: str):
        SetLogLevel(-1)
        self.model_path = model_path or "models/vosk-model-small-en-us-0.15"
        self._model = Model(self.model_path)

    def transcribe_wav(self, audio_path: str) -> str:
        # open the wave file
        wf = wave.open(audio_path, "rb")

        # Verify audio format (Mono, 16-bit PCM)
        if (
            wf.getnchannels() != 1 
            or wf.getsampwidth() != 2 
            or wf.getcomptype() != "NONE"
        ):
            logger.error("Audio file must be WAV format mono PCM.")
            raise ValueError(
                "Expected mono, 16-bit, 16kHz PCM WAV audio."
            )

        # 3. Initialize the recognizer with the audio's sample rate (e.g., 16000)
        recognizer = KaldiRecognizer(
            self._model,
            wf.getframerate()
        )

        results = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break

            if recognizer.AcceptWaveform(data):
                part = json.loads(recognizer.Result())
                if part.get("text"):
                    results.append(part.get("text", ""))

        # 5. Get the final remaining words
        final_part = json.loads(recognizer.FinalResult())
        results.append(final_part.get("text", ""))  


        transcription = " ".join(results).strip()
        logger.debug(f"Transcription results: {transcription}")
        return transcription

