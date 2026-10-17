import asyncio
import os
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from MusicPlayer import MusicPlayer

load_dotenv()

SUPPORTED_FORMATS = ('.mp3', '.wav', '.ogg', '.flac', '.m4a', '.opus')
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
PREFIX = os.getenv('DISCORD_BOT_PREFIX') or '/'
MUSIC_FOLDER = os.getenv('DISCORD_BOT_MUSIC_SOURCE_FOLDER') or "music"
DEBUG = (os.getenv('DISCORD_BOT_DEBUG') or '').lower() in ('1', 'true', 'yes')

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)
Path(MUSIC_FOLDER).mkdir(exist_ok=True)

music_players = {} # Global dict for storing players to servers

def get_player(guild_id):
    if guild_id not in music_players:
        music_players[guild_id] = MusicPlayer(MUSIC_FOLDER,SUPPORTED_FORMATS)
    return music_players[guild_id]

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

async def track_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    files = get_music_files()
    choices: list[app_commands.Choice[str]] = []
    current_lower = current.lower()

    for index, filename in enumerate(files, start=1):
        if current and current_lower not in filename.lower() and current != str(index):
            continue
        label = f"{index}. {filename}"[:100]
        choices.append(app_commands.Choice(name=label, value=str(index)))
        if len(choices) >= 25:
            break

    return choices

REPEAT_MODE_CHOICES = [
    app_commands.Choice(name="Repeat current track", value="repeat"),
    app_commands.Choice(name="Repeat playlist", value="repeat_playlist"),
    app_commands.Choice(name="No repeat", value="no_repeat"),
]

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

@bot.hybrid_command(
    name="ping",
    description="Check if the bot is online",
    brief="Check if the bot is online",
    usage="ping",
)
async def ping(ctx):
    """Basic check if bot is alive"""
    latency = round(bot.latency * 1000)
    await ctx.send(f'Pong. Latency: {latency} ms')

@bot.command()
async def info(ctx):
    """Gather bot info on this server"""
    embed = discord.Embed(
        title="Bot info",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="Server",
        value=f"**Name:** {ctx.guild.name}\n"
              f"**ID:** {ctx.guild.id}\n"
              f"**Members:** {ctx.guild.member_count}",
        inline=False
    )

    bot_member = ctx.guild.get_member(bot.user.id)
    permissions = ctx.channel.permissions_for(bot_member)

    embed.add_field(
        name="Bot permissions",
        value=f"**Read messages:** {'yes' if permissions.read_messages else 'no'}\n"
              f"**Send messages:** {'yes' if permissions.send_messages else 'no'}\n"
              f"**Manage messages:** {'yes' if permissions.manage_messages else 'no'}\n"
              f"**Read history:** {'yes' if permissions.read_message_history else 'no'}",
        inline=False
    )

    await ctx.send(embed=embed)

@bot.command()
async def debug(ctx):
    """Gather debugging info"""
    await ctx.send(f'''
**Debug:**
Bot: {bot.user}
Bot ID: {bot.user.id}
Prefix: {PREFIX}
Latency: {round(bot.latency * 1000)}ms
Channel: #{ctx.channel.name}
Server: {ctx.guild.name}
Message ID: {ctx.message.id}
    ''')

@bot.command()
async def channels(ctx):
    """Show all channels"""
    try:
        text_channels = [c for c in ctx.guild.text_channels]
        voice_channels = [c for c in ctx.guild.voice_channels]

        embed = discord.Embed(
            title="Server channels",
            color=discord.Color.green()
        )

        if text_channels:
            embed.add_field(
                name="Text channels",
                value="\n".join([f"- {c.name} ({c.id})" for c in text_channels[:10]]),
                inline=False
            )

        if voice_channels:
            embed.add_field(
                name="Voice channels",
                value="\n".join([f"- {c.name}" for c in voice_channels[:5]]),
                inline=False
            )

        await ctx.send(embed=embed)

    except discord.Forbidden:
        await ctx.author.send("Not enough permissions to send messages to this channel")

    except Exception as e:
        error_embed = discord.Embed(title="Execution failure", description=str(e), color=discord.Color.red())
        try:
            await ctx.send(embed=error_embed)
        except discord.Forbidden:
            await ctx.author.send(f"Error. Also not enough permissions to send messages to this channel: `{e}`")

@bot.hybrid_command(
    name="join",
    description="Join your voice channel",
    brief="Join your voice channel",
    usage="join",
)
async def join(ctx):
    """Join to user's voice channel"""
    if ctx.interaction is not None:
        await ctx.defer()
    if not ctx.author.voice:
        await ctx.send("You are not in a voice channel")
        return

    channel = ctx.author.voice.channel

    if ctx.voice_client:
        await ctx.voice_client.move_to(channel)
    else:
        await channel.connect()

    await ctx.send(f"Joined to **{channel.name}**")

@bot.hybrid_command(
    name="leave",
    description="Leave the voice channel",
    brief="Leave the voice channel",
    usage="leave",
)
async def leave(ctx):
    """Leave voice channel"""
    if not ctx.voice_client:
        await ctx.send("Not in a voice channel")
        return

    player = get_player(ctx.guild.id)
    player.stop_requested = True
    player.clear_queue()

    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
    else:
        player.stop_requested = False

    await ctx.voice_client.disconnect()
    await ctx.send("Leaving")

@bot.hybrid_command(
    name="play",
    description="Play a track by number or name",
    brief="Play a track by number or name",
    usage="play <number|filename>",
    help=f"Play from the music folder. Examples: `{PREFIX}play 1`, `{PREFIX}play song name`. Use `{PREFIX}list` to see tracks.",
)
@app_commands.describe(arg="Track number from list or part of the filename")
@app_commands.autocomplete(arg=track_autocomplete)
async def play(ctx, *, arg: str = None):
    """Play track by number or name"""
    if ctx.interaction is not None:
        await ctx.defer()

    if not ctx.author.voice:
        await ctx.send("Enter to the voice channel")
        return

    if not ctx.voice_client:
       # await ctx.invoke(bot.get_command('join'))
       channel = ctx.author.voice.channel
       try:
           voice_client = await channel.connect()
       except discord.ClientException as e:
           await ctx.send(f"Cannot connect: {e}")
           return
    elif ctx.voice_client.channel != ctx.author.voice.channel:
        await ctx.voice_client.move_to(ctx.author.voice.channel)

    player = get_player(ctx.guild.id)
    files = get_music_files()

    if not files:
        files = await refresh_music_files()

    if not files:
        await ctx.send(f"There are no music files in `{MUSIC_FOLDER}`")
        return

    if arg is None:
        await ctx.invoke(bot.get_command('list'))
        return

    found_file = find_track(files, arg)

    if not found_file:
        # Track may have been added after the last scan
        files = await refresh_music_files()
        found_file = find_track(files, arg)

    if not found_file:
        await ctx.send(f"Track '{arg}' not found")
        await ctx.invoke(bot.get_command('list'))
        return

    # Adding to queue
    if player.add_to_queue(found_file):
        if not ctx.voice_client.is_playing():
            await play_next(ctx)
        else:
            embed = discord.Embed(
                title="Track added to a queue",
                description=f"**{found_file}**",
                color=discord.Color.green()
            )
            embed.add_field(name="Queue position", value=str(len(player.queue)))
            await ctx.send(embed=embed)
    else:
        # File was removed after the last scan
        await refresh_music_files()
        await ctx.send(f"File '{found_file}' not found. Track list was refreshed, check `{PREFIX}list`")

async def _handle_playback_done(ctx, error, track):
    """Continue queue after a track ends or fails."""
    player = get_player(ctx.guild.id)

    if player.stop_requested:
        player.stop_requested = False
        return

    if error:
        filename = os.path.basename(track)
        player.discard_track(track)
        try:
            await ctx.send(f"Playback error for {filename}: {error}")
        except discord.HTTPException:
            print(f"Playback error for {filename}: {error}")

    await play_next(ctx, previous_track=track)

async def play_next(ctx, previous_track=None):
    """Play next track form queue. Does not announce a track that just finished and starts again (repeat mode)"""
    player = get_player(ctx.guild.id)
    voice_client = ctx.voice_client

    if not voice_client:
        return

    next_track = player.get_next()

    if next_track:
        try:
            # Настраиваем FFmpeg с правильными опциями
            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(
                    next_track,
                    options='-vn -b:a 128k -ar 44100 -ac 2'
                ),
                volume=player.volume
            )

            def after_playback(error):
                asyncio.run_coroutine_threadsafe(
                    _handle_playback_done(ctx, error, next_track),
                    bot.loop
                )

            voice_client.play(source, after=after_playback)

            if next_track == previous_track and player.play_mode != 'no_repeat':
                return

            filename = os.path.basename(next_track)
            embed = discord.Embed(
                title="Now playing",
                description=f"**{filename}**",
                color=discord.Color.green()
            )
            embed.add_field(name="Volume", value=f"{int(player.volume * 100)}%")
            embed.add_field(name="Queue contains", value=f"{len(player.queue)} tracks")
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"Playing error: {e}")
            player.discard_track(next_track)
            await play_next(ctx)
    else:
        await ctx.send("Queue is empty")

@bot.hybrid_command(
    name="stop",
    description="Stop playback and clear the queue",
    brief="Stop playback and clear the queue",
    usage="stop",
)
async def stop(ctx):
    """Stop playing the music and clear the queue"""
    player = get_player(ctx.guild.id)
    player.stop_requested = True
    player.clear_queue()

    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
    else:
        player.stop_requested = False

    await ctx.send("Music stopped. Queue cleared.")

@bot.hybrid_command(
    name="skip",
    description="Skip the current track",
    brief="Skip the current track",
    usage="skip",
)
async def skip(ctx):
    """Skip the current track"""
    if not ctx.author.voice:
        await ctx.send("Enter to the voice channel")
        return

    if not ctx.voice_client or not (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
        await ctx.send("Nothing is playing")
        return

    player = get_player(ctx.guild.id)
    player.current = None
    ctx.voice_client.stop()
    await ctx.send("Skipped")

TRACKS_PER_PAGE = 20
EMBED_DESCRIPTION_LIMIT = 4096

def build_track_pages(files):
    """Split numbered track list into pages that fit in an embed description"""
    pages = []
    lines = []
    length = 0

    for i, filename in enumerate(files, 1):
        line = f"`{i}.` {discord.utils.escape_markdown(filename)}"[:EMBED_DESCRIPTION_LIMIT]
        if lines and (len(lines) >= TRACKS_PER_PAGE or length + len(line) + 1 > EMBED_DESCRIPTION_LIMIT):
            pages.append("\n".join(lines))
            lines = []
            length = 0
        lines.append(line)
        length += len(line) + 1

    if lines:
        pages.append("\n".join(lines))
    return pages

class TrackListView(discord.ui.View):
    """Previous/Next buttons for paging through the track list"""
    def __init__(self, pages, total):
        super().__init__(timeout=180)
        self.pages = pages
        self.total = total
        self.page = 0
        self.message = None
        self._update_buttons()

    def build_embed(self):
        embed = discord.Embed(
            title="Available tracks",
            description=self.pages[self.page],
            color=discord.Color.blue()
        )
        embed.set_footer(
            text=f"Page {self.page + 1}/{len(self.pages)} · Total: {self.total} files · "
                 f"Play with /play track:<number> or {PREFIX}play <number|name>"
        )
        return embed

    def _update_buttons(self):
        self.previous_page.disabled = self.page == 0
        self.next_page.disabled = self.page >= len(self.pages) - 1

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page -= 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    async def on_timeout(self):
        # Removing buttons once they stop responding
        if self.message:
            try:
                await self.message.edit(view=None)
            except discord.HTTPException:
                pass

@bot.hybrid_command(
    name="list",
    description="Show all tracks in the music folder",
    brief="Show all tracks in the music folder",
    usage="list",
)
async def list(ctx):
    """Show all tracks"""
    files = get_music_files()

    if not files:
        await ctx.send(f"There are no music files in `{MUSIC_FOLDER}`. Please either change folder or add music files in {SUPPORTED_FORMATS} formats in selected folder ")
        return

    view = TrackListView(build_track_pages(files), len(files))

    if len(view.pages) == 1:
        await ctx.send(embed=view.build_embed())
        return

    view.message = await ctx.send(embed=view.build_embed(), view=view)

@bot.hybrid_command(
    name="rescan",
    description="Rescan the music folder for added or removed tracks",
    brief="Rescan the music folder",
    usage="rescan",
)
async def rescan(ctx):
    """Rescan the music folder"""
    if ctx.interaction is not None:
        await ctx.defer()
    files = await refresh_music_files()
    await ctx.send(f"Music folder rescanned. Found {len(files)} files")

@bot.hybrid_command(
    name="playing",
    description="Show the currently playing track",
    brief="Show the currently playing track",
    usage="playing",
)
async def playing(ctx):
    """Show current track name"""
    player = get_player(ctx.guild.id)

    if not player.current:
        await ctx.send("Nothing playing")
        return

    current_name = os.path.basename(player.current)
    voice_client = ctx.voice_client

    embed = discord.Embed(
        title="Now playing",
        color=discord.Color.blue()
    )

    embed.add_field(name="Track", value=f"**{current_name}**", inline=False)

    if voice_client:
        status = "Playing" if voice_client.is_playing() else "Paused"
        embed.add_field(name="Status", value=status, inline=True)

    embed.add_field(name="Volume", value=f"{int(player.volume * 100)}%", inline=True)
    embed.add_field(name="Tracks in queue", value=f"{len(player.queue)}", inline=True)

    await ctx.send(embed=embed)

@bot.hybrid_command(
    name="volume",
    description="Show or set playback volume (0-100)",
    brief="Show or set volume (0-100)",
    usage="volume [0-100]",
    help=f"Show current volume with `{PREFIX}volume`, or set it with `{PREFIX}volume 75`.",
)
@app_commands.describe(level="Volume 0-100; leave empty to show current volume")
async def volume(ctx, level: app_commands.Range[int, 0, 100] = None):
    """Change volume percentage (0-100)"""
    if level is None:
        player = get_player(ctx.guild.id)
        await ctx.send(f"Current volume: {int(player.volume * 100)}%")
        return

    if not 0 <= level <= 100:
        await ctx.send("Volume must be in range from 0 to 100!")
        return

    player = get_player(ctx.guild.id)
    player.volume = level / 100

    # Меняем громкость текущего трека
    if ctx.voice_client and ctx.voice_client.source:
        ctx.voice_client.source.volume = player.volume

    await ctx.send(f"Current volume is set to {level}%")

@bot.hybrid_command(
    name="play_mode",
    description="Set repeat mode for playback",
    brief="Set repeat mode",
    usage="play_mode <repeat|repeat_playlist|no_repeat>",
    help=f"Modes: `repeat`, `repeat_playlist`, `no_repeat`. Example: `{PREFIX}play_mode repeat`.",
)
@app_commands.describe(arg="How tracks repeat after they finish")
@app_commands.choices(arg=REPEAT_MODE_CHOICES)
async def play_mode(ctx, *, arg: str = None):
    """Set playing mode: repeat, repeat_playlist, no_repeat"""
    REPEAT_MODES = ('repeat', 'repeat_playlist', 'no_repeat')
    if not ctx.author.voice:
        await ctx.send("Enter to the voice channel")
        return
    player = get_player(ctx.guild.id)
    if arg not in REPEAT_MODES:
        await ctx.send(f"Wrong repeat mode. Repeat modes are:{REPEAT_MODES}")
        return
    player.play_mode = arg
    await ctx.send(f"Play mode set to **{arg}**")

# Starting
if __name__ == "__main__":
    print(f"Bot starting. Token: {'set' if TOKEN else 'not set'}. Prefix: {PREFIX}. Debug: {'on' if DEBUG else 'off'}")

    if not TOKEN:
        print("Error: DISCORD_BOT_TOKEN is not set")
        print("Create a .env file (see .env.example) and add:")
        print("DISCORD_BOT_TOKEN=your token here")
        raise SystemExit(1)

    if not os.path.exists(MUSIC_FOLDER):
        print(f"Creating folder {MUSIC_FOLDER}")
        os.makedirs(MUSIC_FOLDER)

    bot.run(TOKEN)