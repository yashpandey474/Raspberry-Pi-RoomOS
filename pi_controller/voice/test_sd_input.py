import sounddevice as sd

print(sd.query_devices())
print(sd.query_devices(kind="input"))

sd.check_input_settings(
    samplerate=16000,
    channels=1,
    dtype="int16",
)

print("Input configuration supported")