import asyncio
import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

from MusicPlayer import MusicPlayer

load_dotenv()

SUPPORTED_FORMATS = ('.mp3', '.wav', '.ogg', '.flac', '.m4a', '.opus')
TOKEN = os.getenv('DISCORD_BOT_TOKEN') or 'DEFAULT_DISCORD_BOT_TOKEN'
PREFIX = os.getenv('DISCORD_BOT_PREFIX') or '!'
MUSIC_FOLDER = os.getenv('DISCORD_BOT_MUSIC_SOURCE_FOLDER') or "music"

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

@bot.event
async def on_ready():
    """Checkin if bot see the server"""
    print(f'Bot {bot.user} started. Id: {bot.user.id} . Servers: {len(bot.guilds)}')

    # Printing servers list
    for guild in bot.guilds:
        print(f'   • {guild.name} (ID: {guild.id}). Members count: {guild.member_count}')
        bot_member = guild.get_member(bot.user.id) # Checking server bot permissions
        if bot_member:
            print(f'     Status: {bot_member.status} . Roles: {len(bot_member.roles)}')
    print('-' * 50)
    print(f'Bot {bot.user} started successfully. Music folder: {MUSIC_FOLDER}/')
    print('=' * 50)

    # Checking music in folder
    player = MusicPlayer(MUSIC_FOLDER,SUPPORTED_FORMATS)
    files = player.get_music_files()
    if files:
        print(f'Found {len(files)} files:')
        for file in files:
            print(f'  • {file}')
    else:
        print(f'No music files fount in folder. Please add music files in {SUPPORTED_FORMATS} formats')
    print('=' * 50)

    print(f'Available commands (prefix: {PREFIX}):')
    for cmd in sorted(bot.commands, key=lambda c: c.name):
        # Retrieving first docstring line or using stab
        desc = cmd.help.split('\n')[0] if cmd.help else "No description"
        print(f'  {PREFIX}{cmd.name:<10} - {desc}')
    print('=' * 50)

    # Changing bot status
    await bot.change_presence(
        activity=discord.Game(name=f"Use {PREFIX}help"),
        status=discord.Status.online
    )

@bot.event
async def on_message(message):
    """Debug: logging all messages"""
    print(f'📨 [{message.guild.name if message.guild else "PM"}] '
          f'{message.author}: {message.content}')

    # Обрабатываем команды
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    """Basic check if bot is alive"""
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong! Latency: {latency} ms')

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
        value=f"**Read messages:** {'✅' if permissions.read_messages else '❌'}\n"
              f"**Send messages:** {'✅' if permissions.send_messages else '❌'}\n"
              f"**Manage messages:** {'✅' if permissions.manage_messages else '❌'}\n"
              f"**Read history:** {'✅' if permissions.read_message_history else '❌'}",
        inline=False
    )

    await ctx.send(embed=embed)

@bot.command()
async def debug(ctx):
    """Gather debugging info"""
    await ctx.send(f'''
**Debug:**
• Bot: {bot.user}
• Bot ID: {bot.user.id}
• Prefix: {PREFIX}
• Latency: {round(bot.latency * 1000)}ms
• Channel: #{ctx.channel.name}
• Server: {ctx.guild.name}
• Message ID: {ctx.message.id}
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
                value="\n".join([f"• {c.name} ({c.id})" for c in text_channels[:10]]),
                inline=False
            )

        if voice_channels:
            embed.add_field(
                name="Voice channels",
                value="\n".join([f"• {c.name}" for c in voice_channels[:5]]),
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

@bot.command()
async def join(ctx):
    """Join to user's voice channel"""
    if not ctx.author.voice:
        await ctx.send("You are not in a voice channel")
        return

    channel = ctx.author.voice.channel

    if ctx.voice_client:
        await ctx.voice_client.move_to(channel)
    else:
        await channel.connect()

    await ctx.send(f"Joined to **{channel.name}**")

@bot.command()
async def leave(ctx):
    """Leave voice channel"""
    if ctx.voice_client:
        # Clearing queue for this channel
        if ctx.guild.id in music_players:
            music_players[ctx.guild.id].clear_queue()

        await ctx.voice_client.disconnect()
        await ctx.send("Leaving")
    else:
        await ctx.send("Not in a voice channel")

@bot.command()
async def play(ctx, *, arg=None):
    """Play track by number or name"""

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
    files = player.get_music_files()

    if not files:
        await ctx.send(f"There are no music files in `{MUSIC_FOLDER}`")
        return

    if arg is None:
        await ctx.invoke(bot.get_command('list'))
        return

    found_file = None

    if arg.isdigit():
        index = int(arg) - 1
        if 0 <= index < len(files):
            found_file = files[index]

    if not found_file:
        arg_lower = arg.lower()
        for file in files:
            if arg_lower in file.lower():
                found_file = file
                break

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
        await ctx.send(f"File '{found_file}' not found ")

async def play_next(ctx):
    """Play next track form queue"""
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

            voice_client.play(
                source,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    play_next(ctx),
                    bot.loop
                ) if not e else None
            )

            # Отправляем информацию о текущем треке
            filename = os.path.basename(next_track)
            embed = discord.Embed(
                title="Not playing",
                description=f"**{filename}**",
                color=discord.Color.green()
            )
            embed.add_field(name="Volume", value=f"{int(player.volume * 100)}%")
            embed.add_field(name="Queue contains", value=f"{len(player.queue)} tracks")
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"Playing error: {e}")
            await play_next(ctx)  # Пропускаем проблемный трек
    else:
        await ctx.send("Queue is empty")

@bot.command()
async def stop(ctx):
    """Stop playing the music and clear the queue"""
    if ctx.voice_client:
        ctx.voice_client.stop()

    player = get_player(ctx.guild.id)
    player.clear_queue()

    await ctx.send("Music stopped. Queue cleared.")

@bot.command()
async def list(ctx):
    """Show all tracks"""
    player = get_player(ctx.guild.id)
    files = player.get_music_files()

    if not files:
        await ctx.send(f"There are no music files in `{MUSIC_FOLDER}. Please either change folder or add music files in {SUPPORTED_FORMATS} formats in selected folder ")
        return

    embed = discord.Embed(
        title="Available tracks",
        description=f"Total: {len(files)} files",
        color=discord.Color.blue()
    )

    # Разбиваем на страницы по 10 файлов
    for i, filename in enumerate(files, 1):
        embed.add_field(
            name=f"{i}. {filename}",
            value=f"`{PREFIX}play {i}` OR `{PREFIX}play {filename}`",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command()
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

@bot.command()
async def volume(ctx, level: int = None):
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

@bot.command()
async def play_mode(ctx, *, arg=None):
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

# Starting
if __name__ == "__main__":
    print("Bot starting...")
    print(f"Used token: {'set' if TOKEN else 'not set'}")
    print(f"Used prefix: {PREFIX}")
    print(f"Music folder: {os.path.abspath(MUSIC_FOLDER)}")
    print("Initializing music bot...")

    if not os.path.exists(MUSIC_FOLDER):
        print(f"Creating folder {MUSIC_FOLDER}")
        os.makedirs(MUSIC_FOLDER)

    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Error: token not found")
        print("Please create .env file and add data: ")
        print("DISCORD_BOT_TOKEN=your token here")