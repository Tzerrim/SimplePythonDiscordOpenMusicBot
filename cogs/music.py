import asyncio
import os

import discord
from discord import app_commands
from discord.ext import commands

from config import BITRATE, MUSIC_FOLDER, PREFIX, SUPPORTED_FORMATS
from library import find_track, get_music_files, refresh_music_files
from MusicPlayer import MusicPlayer
from views import TrackListView, build_track_pages


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

class Music(commands.Cog):
    """Music playback commands"""
    def __init__(self, bot):
        self.bot = bot
        self.music_players = {} # Players per server

    def get_player(self, guild_id):
        if guild_id not in self.music_players:
            self.music_players[guild_id] = MusicPlayer(MUSIC_FOLDER, SUPPORTED_FORMATS)
        return self.music_players[guild_id]

    def stop_playback(self, ctx):
        """Clear the queue and stop the current track without starting the next one"""
        player = self.get_player(ctx.guild.id)
        player.clear_queue()

        voice_client = ctx.voice_client
        if voice_client and (voice_client.is_playing() or voice_client.is_paused()):
            # Playback callback sees the flag and does not continue the queue
            player.stop_requested = True
            voice_client.stop()

    async def _handle_playback_done(self, ctx, error, track):
        """Continue queue after a track ends or fails."""
        player = self.get_player(ctx.guild.id)

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

        await self.play_next(ctx, previous_track=track)

    async def play_next(self, ctx, previous_track=None):
        """Play next track form queue. Does not announce a track that just finished and starts again (repeat mode)"""
        player = self.get_player(ctx.guild.id)
        voice_client = ctx.voice_client

        if not voice_client:
            return

        next_track = player.get_next()

        if next_track:
            try:
                source = discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(
                        next_track,
                        options='-vn'
                    ),
                    volume=player.volume
                )

                def after_playback(error):
                    asyncio.run_coroutine_threadsafe(
                        self._handle_playback_done(ctx, error, next_track),
                        self.bot.loop
                    )

                voice_client.play(source, after=after_playback, bitrate=BITRATE)

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
                await self.play_next(ctx)
        else:
            await ctx.send("Queue is empty")

    @commands.hybrid_command(
        name="join",
        description="Join your voice channel",
        brief="Join your voice channel",
        usage="join",
    )
    async def join(self, ctx):
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

    @commands.hybrid_command(
        name="leave",
        description="Leave the voice channel",
        brief="Leave the voice channel",
        usage="leave",
    )
    async def leave(self, ctx):
        """Leave voice channel"""
        if not ctx.voice_client:
            await ctx.send("Not in a voice channel")
            return

        self.stop_playback(ctx)
        await ctx.voice_client.disconnect()
        await ctx.send("Leaving")

    @commands.hybrid_command(
        name="play",
        description="Play a track by number or name",
        brief="Play a track by number or name",
        usage="play <number|filename>",
        help=f"Play from the music folder. Examples: `{PREFIX}play 1`, `{PREFIX}play song name`. Use `{PREFIX}list` to see tracks.",
    )
    @app_commands.describe(arg="Track number from list or part of the filename")
    @app_commands.autocomplete(arg=track_autocomplete)
    async def play(self, ctx, *, arg: str | None = None):
        """Play track by number or name"""
        if ctx.interaction is not None:
            await ctx.defer()

        if not ctx.author.voice:
            await ctx.send("Enter to the voice channel")
            return

        if not ctx.voice_client:
            channel = ctx.author.voice.channel
            try:
                await channel.connect()
            except discord.ClientException as e:
                await ctx.send(f"Cannot connect: {e}")
                return
        elif ctx.voice_client.channel != ctx.author.voice.channel:
            await ctx.voice_client.move_to(ctx.author.voice.channel)

        player = self.get_player(ctx.guild.id)
        files = get_music_files()

        if not files:
            files = await refresh_music_files()

        if not files:
            await ctx.send(f"There are no music files in `{MUSIC_FOLDER}`")
            return

        if arg is None:
            await ctx.invoke(self.bot.get_command('list'))
            return

        found_file = find_track(files, arg)

        if not found_file:
            # Track may have been added after the last scan
            files = await refresh_music_files()
            found_file = find_track(files, arg)

        if not found_file:
            await ctx.send(f"Track '{arg}' not found")
            await ctx.invoke(self.bot.get_command('list'))
            return

        # Adding to queue
        if player.add_to_queue(found_file):
            if not ctx.voice_client.is_playing():
                await self.play_next(ctx)
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

    @commands.hybrid_command(
        name="stop",
        description="Stop playback and clear the queue",
        brief="Stop playback and clear the queue",
        usage="stop",
    )
    async def stop(self, ctx):
        """Stop playing the music and clear the queue"""
        self.stop_playback(ctx)
        await ctx.send("Music stopped. Queue cleared.")

    @commands.hybrid_command(
        name="skip",
        description="Skip the current track",
        brief="Skip the current track",
        usage="skip",
    )
    async def skip(self, ctx):
        """Skip the current track"""
        if not ctx.author.voice:
            await ctx.send("Enter to the voice channel")
            return

        if not ctx.voice_client or not (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
            await ctx.send("Nothing is playing")
            return

        player = self.get_player(ctx.guild.id)
        player.current = None
        ctx.voice_client.stop()
        await ctx.send("Skipped")

    @commands.hybrid_command(
        name="list",
        description="Show all tracks in the music folder",
        brief="Show all tracks in the music folder",
        usage="list",
    )
    async def list_tracks(self, ctx):
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

    @commands.hybrid_command(
        name="rescan",
        description="Rescan the music folder for added or removed tracks",
        brief="Rescan the music folder",
        usage="rescan",
    )
    async def rescan(self, ctx):
        """Rescan the music folder"""
        if ctx.interaction is not None:
            await ctx.defer()
        files = await refresh_music_files()
        await ctx.send(f"Music folder rescanned. Found {len(files)} files")

    @commands.hybrid_command(
        name="playing",
        description="Show the currently playing track",
        brief="Show the currently playing track",
        usage="playing",
    )
    async def playing(self, ctx):
        """Show current track name"""
        player = self.get_player(ctx.guild.id)

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

    @commands.hybrid_command(
        name="volume",
        description="Show or set playback volume (0-100)",
        brief="Show or set volume (0-100)",
        usage="volume [0-100]",
        help=f"Show current volume with `{PREFIX}volume`, or set it with `{PREFIX}volume 75`.",
    )
    @app_commands.describe(level="Volume 0-100; leave empty to show current volume")
    async def volume(self, ctx, level: app_commands.Range[int, 0, 100] = None):
        """Change volume percentage (0-100)"""
        if level is None:
            player = self.get_player(ctx.guild.id)
            await ctx.send(f"Current volume: {int(player.volume * 100)}%")
            return

        if not 0 <= level <= 100:
            await ctx.send("Volume must be in range from 0 to 100!")
            return

        player = self.get_player(ctx.guild.id)
        player.volume = level / 100

        # Changing volume of the current track
        if ctx.voice_client and ctx.voice_client.source:
            ctx.voice_client.source.volume = player.volume

        await ctx.send(f"Current volume is set to {level}%")

    @commands.hybrid_command(
        name="play_mode",
        description="Set repeat mode for playback",
        brief="Set repeat mode",
        usage="play_mode <repeat|repeat_playlist|no_repeat>",
        help=f"Modes: `repeat`, `repeat_playlist`, `no_repeat`. Example: `{PREFIX}play_mode repeat`.",
    )
    @app_commands.describe(arg="How tracks repeat after they finish")
    @app_commands.choices(arg=REPEAT_MODE_CHOICES)
    async def play_mode(self, ctx, *, arg: str | None = None):
        """Set playing mode: repeat, repeat_playlist, no_repeat"""
        REPEAT_MODES = ('repeat', 'repeat_playlist', 'no_repeat')
        if not ctx.author.voice:
            await ctx.send("Enter to the voice channel")
            return
        player = self.get_player(ctx.guild.id)
        if arg not in REPEAT_MODES:
            await ctx.send(f"Wrong repeat mode. Repeat modes are:{REPEAT_MODES}")
            return
        player.play_mode = arg
        await ctx.send(f"Play mode set to **{arg}**")

async def setup(bot):
    await bot.add_cog(Music(bot))
