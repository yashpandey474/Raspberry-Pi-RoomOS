from pi_controller.core.conversation_service import ConversationService
from pi_controller.voice.audio_capture import SoundDeviceAudioCapture
from pi_controller.voice.stt import VoskSTT
from pi_controller.voice.tts import PiperTTS
from pi_controller.voice.audio_output import SoundDeviceAudioOutput

import logging
import asyncio
import tempfile
from pathlib import Path

from shared.contracts import AssistantChatRequest, ChatResponse


logger = logging.getLogger(__name__)
class VoiceAssistant:
    def __init__(
            self, 
            conversation_service: ConversationService,
            audio_capture: SoundDeviceAudioCapture, 
            stt: VoskSTT, 
            audio_output: SoundDeviceAudioOutput, 
            tts: PiperTTS,
        ):
        self.audio_capture = audio_capture
        self.stt = stt
        self.audio_output = audio_output
        self.tts = tts
        self.conversation_service = conversation_service
        # Prevent simultaneous voice interactions
        self._run_lock = asyncio.Lock()

    async def run_once(self, session_id: str) -> None:
        async with self._run_lock:
            with tempfile.TemporaryDirectory(prefix="roomos-voice-") as temp_dir:
                    recording_path = str(Path(temp_dir) / "recording.wav")
                    response_path = str(Path(temp_dir) / "response.wav")

                    # Record audio from microphone
                    await asyncio.to_thread(
                        self.audio_capture.record_wav,
                        recording_path, 
                        duration_seconds=5
                    )

                    logger.info(f"Recording complete. Saved to {recording_path}")

                    # Transcribe it
                    try:
                        text: str = await asyncio.to_thread(
                            self.stt.transcribe_wav,
                            recording_path,
                        )                    
                        logger.info(f"Transcription: {text}")
                    except Exception as e:
                        logger.error(f"Error during transcription: {e}")
                        return

                    if not text or not text.strip():
                        logger.warning("No speech detected in the recording.")
                        return

                    try:
                        chat_response: ChatResponse = await self.conversation_service.chat(
                            AssistantChatRequest(
                                session_id=session_id,
                                message=text,
                            )
                        )
                    except Exception as e:
                        logger.error(f"Encountered an exception while trying to generate a response: {e}")
                        return

                    response_text = (chat_response.response or "").strip()

                    if not response_text:
                        logger.error("AI Engine returned an empty response for session %s", session_id)
                        return


                    # 3. Generate a spoken response
                    await asyncio.to_thread(
                        self.tts.synthesize,
                        response_text, 
                        response_path
                    )
                    
                    logger.info(f"Response generated and saved to {response_path}")

                    # 4. Play through the default speaker
                    await asyncio.to_thread(
                        self.audio_output.play_wav, 
                        response_path
                    )
                    logger.info(f"Response played through default speaker")
