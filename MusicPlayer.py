import os

class MusicPlayer:
    def __init__(self, music_folder, supported_formats,play_mode):
        self.queue = []
        self.current = None
        self.volume = 0.5
        self.music_folder = music_folder
        self.supported_formats = supported_formats
        self.play_mode = play_mode

    def get_music_files(self):
        """Get a list of music files"""
        files = []
        # Проверяем, что папка существует
        if not os.path.isdir(self.music_folder):
            return files

        # Перебираем файлы в папке, а не символы пути
        for file in os.listdir(self.music_folder):
            if file.lower().endswith(self.supported_formats):
                files.append(file)
        return sorted(files)

    def add_to_queue(self, filename):
        """Add file into a queue"""
        filepath = os.path.join(self.music_folder, filename)
        if os.path.exists(filepath):
            self.queue.append(filepath)
            return True
        return False

    def get_next(self):
        """Get next track"""
        if self.queue:
            match self.play_mode:
                case 'repeat_playlist':
                    self.queue.append(self.current)
                    self.current = self.queue.pop(0)
                    return self.current
                case 'repeat':
                    return self.current
                case _:
                    self.current = self.queue.pop(0)
                    return self.current
        self.current = None
        return None

    def clear_queue(self):
        """Clear queue"""
        self.queue.clear()
        self.current = None