import os
from pathlib import Path
from typing import List, Optional


class MusicPlayer:
    def __init__(self, music_folder: str, supported_formats: tuple, play_mode: str = "no_repeat"):
        self.queue: List[str] = []
        self.current: Optional[str] = None
        self.volume: float = 0.5
        self.music_folder = Path(music_folder)
        self.supported_formats = supported_formats
        self.play_mode = play_mode

    def get_music_files(self) -> List[str]:
        """Retrieving all music files from folder ordered"""
        if not self.music_folder.is_dir():
            return []
        files = [
            f.name for f in self.music_folder.iterdir()
            if f.is_file() and f.suffix.lower() in self.supported_formats
        ]
        return sorted(files)

    def add_to_queue(self, filename: str) -> bool:
        """Adding file to queue"""
        filepath = self.music_folder / filename
        if filepath.exists():
            self.queue.append(str(filepath))
            return True
        return False

    def get_next(self) -> Optional[str]:
        """Retrieving next music file to play"""
        if not self.queue:
            self.current = None
            return None

        match self.play_mode:
            case 'repeat_playlist':
                self.queue.append(self.current)
                self.current = self.queue.pop(0)
            case 'repeat':
                pass  # self.current остается прежним
            case _:  # no_repeat
                self.current = self.queue.pop(0)

        return self.current

    def clear_queue(self):
        """Clearing queue and current playing track"""
        self.queue.clear()
        self.current = None