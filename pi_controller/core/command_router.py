from pi_controller.media.service import MediaService
import logging
import re

logger = logging.getLogger(__name__)

increase_volume_commands = ("increase volume", "turn up volume", "raise volume")
decrease_volume_commands = ("decrease volume", "turn down volume", "lower volume")


volume_match_re = r"set volume to (\d{1,3})"

class CommandRouter:
    def __init__(self, media_service: MediaService):
        self.media_service = media_service
        self.command_mapping = {
            ("play some music", "play any music"): self.media_service.play,
            ("pause the music", "pause", "pause music"): self.media_service.pause,
            ("next song", "play the next song", "next", "next song please"): self.media_service.next,
            ("previous song", "play previous song", "play the previous song", "previous"): self.media_service.previous,
            increase_volume_commands + decrease_volume_commands: self.media_service.set_volume,
        }

    def handle(self, message: str) -> str | None:
        if not message:
            logger.error(f"No message sent to command router!")
            return None
        message = message.lower().strip()

        volume_match = re.fullmatch(
            volume_match_re,
            message
        )

        if volume_match:
            volume = int(volume_match.group(1))
            if not 0 <= volume <= 100:
                return "Volume must be between 0 and 100."

            state = self.media_service.set_volume(volume)
            return f"Volume set to {state.volume}%"
        
        for k, v in self.command_mapping.items():
            if message in k:
                logger.info(f"Command matched: {message}. Executing: {v.__name__}")
                if v == self.media_service.set_volume:
                    if message in increase_volume_commands:
                        current_state = self.media_service.get_state()
                        new_volume = min(current_state.volume + 10, 100)
                        v(self.media_service, new_volume)
                        return f"Executed command: {v.__name__} with volume {new_volume}"
                    else:
                        current_state = self.media_service.get_state()
                        new_volume = max(current_state.volume - 10, 0)
                        v(self.media_service, new_volume)
                        return f"Executed command: {v.__name__} with volume {new_volume}"
                else:
                    v()
                    return f"Executed command: {v.__name__}"

        logger.info(f"No command matched for message: {message}")
        return None

            