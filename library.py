import asyncio

from config import MUSIC_FOLDER, SUPPORTED_FORMATS
from MusicPlayer import MusicPlayer

music_files_cache = None # Sorted track list shared by all servers

def get_music_files():
    """Cached track list. Scans the folder only if the cache is still empty"""
    global music_files_cache
    if music_files_cache is None:
        music_files_cache = MusicPlayer(MUSIC_FOLDER, SUPPORTED_FORMATS).get_music_files()
    return music_files_cache

async def refresh_music_files():
    """Rescan the music folder in a thread so a slow disk or NAS does not block the bot"""
    global music_files_cache
    scanner = MusicPlayer(MUSIC_FOLDER, SUPPORTED_FORMATS)
    music_files_cache = await asyncio.to_thread(scanner.get_music_files)
    return music_files_cache

def find_track(files, arg):
    """Find track by number from list or by part of the filename"""
    if arg.isdigit():
        index = int(arg) - 1
        if 0 <= index < len(files):
            return files[index]

    arg_lower = arg.lower()
    for file in files:
        if arg_lower in file.lower():
            return file
    return None
