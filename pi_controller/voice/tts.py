import subprocess
import sys

class PiperTTS:
    """
    Piper runs fast, offline neural text-to-speech locally on standard CPUs or with GPU acceleration
    """
    def __init__(self, model_path: str):
        self.model_path = model_path

    def synthesize(self, text: str, output_path: str) -> None:
        """
        Guarantees Piper runs using the same Python environment as RoomOS, rather than accidentally invoking another installation.
        """
        if not text or not text.strip():
            raise ValueError("Text for synthesis cannot be empty.")
        if not output_path:
            raise ValueError("Output path for synthesized audio cannot be empty.")

        try:
            subprocess.run(
                [
                    sys.executable,
                    "-m", "piper",
                    "-m", self.model_path,
                    "-f", output_path,
                    "--", text,
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=30
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Piper TTS synthesis failed: {e.stderr}") from e