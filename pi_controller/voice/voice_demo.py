from pi_controller.voice.audio_capture import SoundDeviceAudioCapture
from pi_controller.voice.audio_output import SoundDeviceAudioOutput
from pi_controller.voice.stt import VoskSTT
from pi_controller.voice.tts import PiperTTS
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def main():
    capture = SoundDeviceAudioCapture()
    stt = VoskSTT(model_path="models/stt/vosk-model-small-en-us-0.15")
    audio_output = SoundDeviceAudioOutput()
    tts = PiperTTS(model_path="models/tts/en_US-lessac-medium")

    logger.info(f"All classes initialised")

    # 1. Record five seconds of microphone input
    capture.record_wav("recording.wav", duration_seconds=5)

    logger.info(f"Recording complete. Saved to recording.wav")

    # 2. Transcribe it
    text = stt.transcribe_wav("recording.wav")
    logger.info(f"Transcription: {text}")

    # 3. Generate a spoken response
    tts.synthesize(
        f"You said: {text}",
        "response.wav"
    )
    logger.info(f"Response generated and saved to response.wav")

    # 4. Play through the default speaker
    audio_output.play_wav("response.wav")
    logger.info(f"Response played through default speaker")

if __name__ == "__main__":
    main()