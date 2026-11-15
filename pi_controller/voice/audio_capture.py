import sounddevice as sd
import wave
import logging

logger = logging.getLogger(__name__)


class SoundDeviceAudioCapture:

    def __init__(
            self, 
            default_recording_duration: int = 5,
            sample_rate: int = 16000, 
            channels: int = 1, 
            sample_width: int = 2,
            chunk_size: int = 4000
        ):
        self.default_recording_duration = default_recording_duration
        self.sample_rate = sample_rate
        self.channels = channels
        self.dtype = f'int{sample_width * 8}'
        self.sample_width = sample_width
        self.chunk_size = chunk_size


    def record_wav(
        self,
        output_path: str,
        duration_seconds: int | None = None
    ) -> None:
        if duration_seconds is None:
            duration_seconds = self.default_recording_duration
            logger.info(f"No duration specified. Using default: {duration_seconds} seconds.")

        if duration_seconds <= 0:
            logger.error("Duration must be a positive integer.")
            raise ValueError("Duration must be a positive integer.")
        
        total_frames = int(self.sample_rate * duration_seconds)
        frames_recorded = 0

        with wave.open(output_path, "w") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.sample_width)
            wf.setframerate(self.sample_rate)
            logger.info(f"Recording audio for {duration_seconds} seconds at {self.sample_rate} Hz, {self.channels} channel(s), {self.sample_width * 8}-bit PCM.")
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
                blocksize=self.chunk_size,
            ) as stream:
                logger.info("Microphone stream opened.")
                while frames_recorded < total_frames:
                    logger.debug("Reading audio frames...")
                    # Read either the full chunk_size or just the remaining frames needed
                    frames_to_read = min(
                        self.chunk_size, 
                        total_frames - frames_recorded
                    )
                    data, overflowed = stream.read(
                        frames_to_read
                    )
                    logger.debug("Read %d frames.", frames_to_read)
                    if overflowed:
                        logger.warning("Audio buffer overflowed!")
                    wf.writeframes(data)
                    frames_recorded += frames_to_read

        logger.info(f"Recording complete. Saved to {output_path}. Total frames recorded: {frames_recorded}")
