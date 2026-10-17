import os

import discord
from discord.ext import commands

from config import BITRATE, DEBUG, MUSIC_FOLDER, PREFIX, SUPPORTED_FORMATS, TOKEN
from library import refresh_music_files

EXTENSIONS = ('cogs.music', 'cogs.utility')

class MusicBot(commands.Bot):
    async def setup_hook(self):
        """Load command groups before connecting to Discord"""
        for extension in EXTENSIONS:
            await self.load_extension(extension)

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = MusicBot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    """Checkin if bot see the server"""
    print(f'Bot {bot.user} started. Id: {bot.user.id}. Servers: {len(bot.guilds)}')
    for guild in bot.guilds:
        print(f'Server: {guild.name} (ID: {guild.id}), members: {guild.member_count}')

    # Checking music in folder
    files = await refresh_music_files()
    if files:
        print(f'Music folder: {os.path.abspath(MUSIC_FOLDER)}, files: {len(files)}')
    else:
        print(f'No music files found in {os.path.abspath(MUSIC_FOLDER)}. Supported formats: {", ".join(SUPPORTED_FORMATS)}')

    commands_list = ", ".join(cmd.name for cmd in sorted(bot.commands, key=lambda c: c.name))
    print(f'Commands (prefix {PREFIX}): {commands_list}')

    if not getattr(bot, '_slash_synced', False):
        synced = await bot.tree.sync()
        bot._slash_synced = True
        print(f'Synced {len(synced)} slash commands')

    # Changing bot status
    await bot.change_presence(
        activity=discord.Game(name=f"/play or {PREFIX}help"),
        status=discord.Status.online
    )

@bot.event
async def on_message(message):
    """Debug: logging all messages when DISCORD_BOT_DEBUG is enabled"""
    if DEBUG:
        print(f'[{message.guild.name if message.guild else "PM"}] '
              f'{message.author}: {message.content}')

    await bot.process_commands(message)

# Starting
if __name__ == "__main__":
    print(f"Bot starting. Token: {'set' if TOKEN else 'not set'}. Prefix: {PREFIX}. Bitrate: {BITRATE} kbps. Debug: {'on' if DEBUG else 'off'}")

    if not TOKEN:
        print("Error: DISCORD_BOT_TOKEN is not set")
        print("Create a .env file (see .env.example) and add:")
        print("DISCORD_BOT_TOKEN=your token here")
        raise SystemExit(1)

    if not os.path.exists(MUSIC_FOLDER):
        print(f"Creating folder {MUSIC_FOLDER}")
        os.makedirs(MUSIC_FOLDER)

    bot.run(TOKEN)
