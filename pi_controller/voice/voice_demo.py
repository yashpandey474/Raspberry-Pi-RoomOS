from pi_controller.voice.audio_capture import SoundDeviceAudioCapture
from pi_controller.voice.audio_output import SoundDeviceAudioOutput
from pi_controller.voice.stt import VoskSTT

capture = SoundDeviceAudioCapture()
stt = VoskSTT(model_path="models/vosk-model-small-en-us-0.15")
audio_output = SoundDeviceAudioOutput()
d
# 1. Record five seconds of microphone input
capture.record_wav("recording.wav", duration_seconds=5)

# 2. Transcribe it
text = stt.transcribe_wav("recording.wav")
print("You said:", text)

# 3. Generate a spoken response
tts.synthesize(
    f"You said: {text}",
    "response.wav"
)

# 4. Play through the default speaker
audio_output.play_wav("response.wav")