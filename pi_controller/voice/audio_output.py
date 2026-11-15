import wave
import sounddevice as sd
"""
No hardcoded frequency or sample width. Use the values from the WAV file.
"""
class SoundDeviceAudioOutput:

    def play_wav(self, audio_path: str) -> None:
        with wave.open(audio_path, "rb") as wf:
            sample_rate = wf.getframerate()
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()

            if wf.getcomptype() != "NONE":
                raise ValueError("Compressed WAV files are not supported.")

            if sample_width != 2:
                raise ValueError("Only 16-bit PCM WAV files are supported.")

            if channels not in (1, 2):
                raise ValueError("Only mono and stereo audio are supported.")
            
            with sd.RawOutputStream(
                samplerate=sample_rate,
                channels=channels,
                dtype=f'int16',
            ) as stream:
                data = wf.readframes(1024)
                while data:
                    stream.write(data)
                    data = wf.readframes(1024)