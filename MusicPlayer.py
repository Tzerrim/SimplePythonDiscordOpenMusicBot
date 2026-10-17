from pathlib import Path


class MusicPlayer:
    def __init__(self, music_folder: str, supported_formats: tuple, play_mode: str = "no_repeat"):
        self.queue: list[str] = []
        self.current: str | None = None
        self.volume: float = 0.5
        self.music_folder = Path(music_folder)
        self.supported_formats = supported_formats
        self.play_mode = play_mode
        self.stop_requested = False

    def get_music_files(self) -> list[str]:
        """Retrieving all music files from folder and subfolders, sorted."""
        if not self.music_folder.is_dir():
            return []
        files = [
            f.relative_to(self.music_folder).as_posix()
            for f in self.music_folder.rglob('*')
            if f.is_file() and f.suffix.lower() in self.supported_formats
        ]
        return sorted(files)

    def _resolve_track_path(self, track: str) -> Path | None:
        """Resolve a track name or relative path inside the music folder."""
        filepath = (self.music_folder / track).resolve()
        if not filepath.is_file():
            return None
        if filepath.suffix.lower() not in self.supported_formats:
            return None
        try:
            filepath.relative_to(self.music_folder.resolve())
        except ValueError:
            return None
        return filepath

    def add_to_queue(self, track: str) -> bool:
        """Adding file to queue by name or relative path."""
        filepath = self._resolve_track_path(track)
        if filepath is None:
            return False
        self.queue.append(str(filepath))
        return True

    def get_next(self) -> str | None:
        """Retrieving next music file to play"""
        if self.play_mode == 'repeat':
            if self.current:
                return self.current
            if self.queue:
                self.current = self.queue.pop(0)
                return self.current
            return None

        if self.play_mode == 'repeat_playlist':
            if self.queue:
                if self.current:
                    self.queue.append(self.current)
                self.current = self.queue.pop(0)
                return self.current
            if self.current:
                return self.current
            return None

        if not self.queue:
            self.current = None
            return None

        self.current = self.queue.pop(0)
        return self.current

    def clear_queue(self):
        """Clearing queue and current playing track"""
        self.queue.clear()
        self.current = None

    def discard_track(self, track: str):
        """Remove a failed track so it is not retried."""
        if self.current == track:
            self.current = None
        self.queue = [queued for queued in self.queue if queued != track]