from pi_controller.media.contracts import MediaPlayer, Track
from pi_controller.media.contracts import PlaybackState

class FakeMediaPlayer(MediaPlayer):
    def __init__(self, tracks: list[Track]):
        self.tracks = list(tracks)
        self.current_index: int | None = 0
        self._state = PlaybackState(
            status="stopped",
            current_track=None,
            volume=50,
            position_seconds=0
        )
    
    def play(self) -> PlaybackState:
        self._state.status = "playing"
        if self._state.current_track is None and self.tracks:
            self._state.current_track = self.tracks[0]  
            self.current_index = 0          
        return self._state

    def pause(self) -> PlaybackState:
        self._state.status = "paused"
        return self._state

    def next(self) -> PlaybackState:
        # For simplicity, just reset the position and keep the same track
        self._state.position_seconds = 0
        self._state.status = "playing"
        if self.tracks:
            next_index = (self.current_index + 1) % len(self.tracks)
            self._state.current_track = self.tracks[next_index]
            self.current_index = next_index
            print(f"Switched to next track: {self._state.current_track.title} by {self._state.current_track.artist}")

        return self._state

    def previous(self) -> PlaybackState:
        # For simplicity, just reset the position and keep the same track
        self._state.position_seconds = 0
        self._state.status = "playing"

        print(f"Current index before previous: {self.current_index}")
        if self.tracks:
            previous_index = (self.current_index - 1) % len(self.tracks)
            self.current_index = previous_index
            self._state.current_track = self.tracks[previous_index]
            print(f"Switched to previous track: {self._state.current_track.title} by {self._state.current_track.artist}")
        return self._state

    def set_volume(self, volume: int) -> PlaybackState:
        if not 0 <= volume <= 100:
            raise ValueError("Volume must be between 0 and 100")
        self._state.volume = volume
        return self._state

    def get_state(self) -> PlaybackState:
        return self._state.model_copy(deep=True)