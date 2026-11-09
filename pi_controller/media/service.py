from .contracts import MediaPlayer, PlaybackState


class MediaService:
    def __init__(self, player: MediaPlayer):
        self._player = player

    def play(self) -> PlaybackState:
        return self._player.play()

    def pause(self) -> PlaybackState:
        return self._player.pause()

    def next(self) -> PlaybackState:
        return self._player.next()

    def previous(self) -> PlaybackState:
        return self._player.previous()

    def set_volume(self, volume: int) -> PlaybackState:
        if not 0 <= volume <= 100:
            raise ValueError("Volume must be between 0 and 100")

        return self._player.set_volume(volume)

    def get_state(self) -> PlaybackState:
        return self._player.get_state()