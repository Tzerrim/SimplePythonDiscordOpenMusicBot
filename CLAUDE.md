# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A Discord bot (discord.py 2.x) that plays local audio files from a configured folder (scanned recursively) into voice channels. Two source files: `main.py` (bot setup, commands, playback loop) and `MusicPlayer.py` (per-guild queue/state, no Discord dependencies).

## Running

### First run: create the virtual environment

Run once from the project root:

```bash
python3 -m venv .venv            # Windows: python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Next runs: reuse the existing virtual environment

`.venv` stays in the project folder, so don't create it again. Activate it and start the bot:

```bash
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python main.py
```

Or run the venv's Python directly, without activating it:

```bash
.venv/bin/python main.py         # Windows: .venv\Scripts\python main.py
```

Run `deactivate` to leave the venv. Activation applies only to the current terminal, so activate it again in each new terminal.

- FFmpeg must be on `PATH` (used by `discord.FFmpegPCMAudio`).
- Config comes from `.env` via python-dotenv: `DISCORD_BOT_TOKEN` (required), `DISCORD_BOT_PREFIX` (default `/` in code), `DISCORD_BOT_MUSIC_SOURCE_FOLDER` (default `music`, created if missing), `DISCORD_BOT_BITRATE` (Opus kbps passed to `voice_client.play`, default 96, 16-512), `DISCORD_BOT_DEBUG` (`true` prints every chat message to the console).
- There are no tests, linter, or build step. `.env.example` is the config template; keep it in sync with the variables read in `main.py`.

## Checking and updating dependencies

Outdated libraries are a common reason the bot stops working, because Discord changes its gateway and voice protocols. Typical symptoms are voice connection failures, the bot joining but playing nothing, or errors raised inside `discord.py` itself. Run these inside the activated `.venv`:

```bash
pip list --outdated                          # show installed packages with newer versions
pip index versions discord.py                # list versions available on PyPI
pip show discord.py python-dotenv PyNaCl     # show installed versions

pip install --upgrade -r requirements.txt    # upgrade everything in requirements.txt
pip install --upgrade "discord.py[voice]"    # upgrade one package (the [voice] extra pulls in PyNaCl)
```

- `requirements.txt` only sets minimum versions (`>=`), so `pip install --upgrade -r requirements.txt` installs the latest releases. After an upgrade fixes a problem, raise the minimum version in `requirements.txt` to the version that works so new installs don't get an older, broken one.
- After upgrading, run `python main.py` and check startup output (`Synced N slash commands`), then test `/join` and `/play` in Discord. Read the discord.py changelog for breaking changes when the major or minor version changes.
- If a dependency is broken, recreate the environment: delete `.venv`, create it again, and run `pip install -r requirements.txt`.
- FFmpeg is not managed by pip. Update it with the system package manager (`dnf upgrade ffmpeg`, `apt upgrade ffmpeg`, `brew upgrade ffmpeg`, `winget upgrade Gyan.FFmpeg`).

## Architecture

- **Per-guild state**: `music_players` dict in `main.py` maps `guild_id -> MusicPlayer`, created lazily by `get_player()`. All queue, volume, play mode and current-track state lives on `MusicPlayer`.
- **Commands**: user-facing commands use `@bot.hybrid_command` so they work both as prefix commands and slash commands; `info`, `debug`, `channels` are prefix-only (`@bot.command`). Slash commands are synced once in `on_ready` (guarded by `bot._slash_synced`). Hybrid commands that may be slow call `ctx.defer()` when invoked via interaction.
- **Track numbering**: track numbers are 1-based indexes into `MusicPlayer.get_music_files()` (sorted POSIX paths relative to the music folder). `/list`, `play` lookup, and `track_autocomplete` all rely on this same ordering — keep them consistent. `play` matches by number first, then by case-insensitive substring.
- **Playback loop**: `play_next()` pulls `player.get_next()`, wraps it in `PCMVolumeTransformer(FFmpegPCMAudio(...))`, and registers an `after` callback that runs on discord's audio thread and schedules `_handle_playback_done()` back onto `bot.loop` via `asyncio.run_coroutine_threadsafe`. That handler discards failed tracks and calls `play_next()` again.
- **Stop vs. skip**: `stop`/`leave` go through `stop_playback()`, which clears the queue and, only if a track is playing or paused, sets `player.stop_requested = True` before `voice_client.stop()` so the `after` callback does not advance the queue. `skip` instead clears `player.current` so `get_next()` advances even in `repeat` mode.
- **FFmpeg options**: discord.py already outputs 48 kHz stereo PCM and appends our `options` after its own, so never pass `-ar`/`-ac` there; overriding the sample rate makes playback fast and high-pitched.
- **Play modes** (`MusicPlayer.get_next`): `no_repeat` pops the queue; `repeat` keeps returning `current`; `repeat_playlist` rotates `current` to the back of the queue.
- **Path safety**: `MusicPlayer._resolve_track_path` rejects paths that resolve outside the music folder or have unsupported extensions. `SUPPORTED_FORMATS` is defined in `main.py` and passed into `MusicPlayer`.

## Docs

`README.md` (English) and `README_RU.md` (Russian) must stay in sync. Any change to one — new sections, edits, removals, fixes — must be made in the other in the same task, translated, with the same structure and placement.
