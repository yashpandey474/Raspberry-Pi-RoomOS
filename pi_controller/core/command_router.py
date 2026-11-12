from pi_controller.media.service import MediaService
import logging
import re

logger = logging.getLogger(__name__)

increase_volume_commands = ("increase volume", "turn up volume", "raise volume")
decrease_volume_commands = ("decrease volume", "turn down volume", "lower volume")
command_mapping = {
    ("play some music", "play any music"): MediaService.play,
    ("pause the music", "pause", "pause music"): MediaService.pause,
    ("next song", "play the next song", "next", "next song please"): MediaService.next,
    ("previous song", "play previous song", "play the previous song", "previous"): MediaService.previous,
    increase_volume_commands + decrease_volume_commands + ("set volume to 50", "set volume to 75"): MediaService.set_volume,
}
class CommandRouter:
    def __init__(self, media_service: MediaService):
        self.media_service = media_service

    def handle(self, message: str) -> str | None:
        if not message:
            logger.error(f"No message sent to command router!")
            return None
        message = message.lower().strip()
        for k, v in command_mapping.items():
            if message in k:
                logger.info(f"Command matched: {message}. Executing: {v.__name__}")
                if v == MediaService.set_volume:
                    # Extract volume level from the message
                    match = re.search(r'\b(\d{1,3})\b', message)
                    if match:
                        volume_level = int(match.group(1))
                        if 0 <= volume_level <= 100:
                            v(self.media_service, volume_level)
                            return f"Executed command: {v.__name__} with volume {volume_level}"
                        else:
                            logger.error(f"Volume level out of range: {volume_level}")
                            return f"Volume level must be between 0 and 100. Received: {volume_level}"
                    else:
                        if message in increase_volume_commands:
                            current_state = self.media_service.get_state()
                            new_volume = min(current_state.volume + 10, 100)
                            v(self.media_service, new_volume)
                            return f"Executed command: {v.__name__} with volume {new_volume}"
                        elif message in decrease_volume_commands:
                            current_state = self.media_service.get_state()
                            new_volume = max(current_state.volume - 10, 0)
                            v(self.media_service, new_volume)
                            return f"Executed command: {v.__name__} with volume {new_volume}"
                        else:
                            logger.error(f"No volume level found in message: {message}")
                            return "No valid volume level found in the command."
                else:
                    v(self.media_service)
                return f"Executed command: {v.__name__}"

        logger.info(f"No command matched for message: {message}")
        return None

            