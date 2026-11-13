from pi_controller.voice.stt import VoskSTT

stt = VoskSTT(
    model_path="models/stt/vosk-model-small-en-us-0.15"
)

text = stt.transcribe_wav("/Users/kmpandey/Desktop/Projects/Raspberry-pi-roomos/test.wav")

print("Recognized:", text)