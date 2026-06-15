# Discord Open Music Bot

A Discord bot that plays local music files from a folder (including subfolders).

## Requirements

| Component | Version |
|-----------|---------|
| Python | 3.11 or newer |
| FFmpeg | 4.x or newer (8.x recommended) |
| Internet | Required for Discord connection |
| Discord bot token | Required |

### Python packages (installed via pip)

- `discord.py[voice]` — Discord API and voice support
- `python-dotenv` — load settings from `.env`

These are listed in `requirements.txt`.

### System dependency (not installed by pip)

- **FFmpeg** — required for audio playback. Must be installed separately and available in your `PATH`.

---

## Windows

### 1. Install Python

1. Download Python from [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Run the installer
3. Enable **"Add python.exe to PATH"**
4. Verify in Command Prompt or PowerShell:

```bat
python --version
pip --version
```

### 2. Install FFmpeg

**Option A — winget (recommended):**

```bat
winget install Gyan.FFmpeg
```

**Option B — Chocolatey:**

```bat
choco install ffmpeg
```

**Option C — manual:**

1. Download a build from [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)
2. Extract the archive
3. Add the `bin` folder to your system `PATH`

Verify:

```bat
ffmpeg -version
```

### 3. Install and run the bot

```bat
cd path\to\DiscordOpenMusicBot
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and set your Discord bot token and music folder path.

```bat
python main.py
```

---

## Linux

### 1. Install Python

**Fedora / RHEL:**

```bash
sudo dnf install python3 python3-pip
```

**Debian / Ubuntu:**

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**Arch:**

```bash
sudo pacman -S python python-pip
```

Verify:

```bash
python3 --version
pip3 --version
```

### 2. Install FFmpeg

**Fedora / RHEL:**

```bash
sudo dnf install ffmpeg
```

**Debian / Ubuntu:**

```bash
sudo apt install ffmpeg
```

**Arch:**

```bash
sudo pacman -S ffmpeg
```

Verify:

```bash
ffmpeg -version
```

### 3. Install and run the bot

```bash
cd /path/to/DiscordOpenMusicBot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set your Discord bot token and music folder path.

```bash
python main.py
```

### Optional: run as a background service (systemd)

Create `/etc/systemd/system/discord-music-bot.service`:

```ini
[Unit]
Description=Discord Open Music Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/DiscordOpenMusicBot
ExecStart=/path/to/DiscordOpenMusicBot/.venv/bin/python main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable discord-music-bot
sudo systemctl start discord-music-bot
```

---

## macOS

### 1. Install Homebrew (if not installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install Python and FFmpeg

```bash
brew install python ffmpeg
```

Verify:

```bash
python3 --version
ffmpeg -version
```

### 3. Install and run the bot

```bash
cd /path/to/DiscordOpenMusicBot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set your Discord bot token and music folder path.

```bash
python main.py
```

---

## Configuration (.env)

Copy the example file and edit it:

| OS | Command |
|----|---------|
| Windows | `copy .env.example .env` |
| Linux / macOS | `cp .env.example .env` |

### Example `.env` file

Create a file named `.env` in the project root. It should look like this:

```env
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_BOT_PREFIX=!
DISCORD_BOT_MUSIC_SOURCE_FOLDER=music
```

**Minimal example (local `music` folder in the project):**

```env
DISCORD_BOT_TOKEN=MTIzNDU2Nzg5MDEyMzQ1Njc4.GAbCdE.fGhIjKlMnOpQrStUvWxYzAbCdEfGhIj
DISCORD_BOT_PREFIX=!
DISCORD_BOT_MUSIC_SOURCE_FOLDER=music
```

**Windows example (custom music folder):**

```env
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_BOT_PREFIX=!
DISCORD_BOT_MUSIC_SOURCE_FOLDER=D:\Music\MyPlaylist
```

**Linux / macOS example (absolute path):**

```env
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_BOT_PREFIX=!
DISCORD_BOT_MUSIC_SOURCE_FOLDER=/home/user/Music
```

**NAS / network storage example:**

```env
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_BOT_PREFIX=!
DISCORD_BOT_MUSIC_SOURCE_FOLDER=/mnt/nas/Music/Library
```

### Variable reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DISCORD_BOT_TOKEN` | Your bot token from the Discord Developer Portal | `DISCORD_BOT_TOKEN=your_token_here` |
| `DISCORD_BOT_PREFIX` | Command prefix | `!` |
| `DISCORD_BOT_MUSIC_SOURCE_FOLDER` | Path to your music library | `music` or `D:\Music` or `/home/user/Music` |

**Important:**
- Do not commit `.env` to git (it contains your secret token)
- Do not share your token publicly
- Use absolute paths for external drives and NAS mounts
- If a variable is missing, the bot uses defaults: prefix `!`, folder `music`

Supported audio formats: `.mp3`, `.wav`, `.ogg`, `.flac`, `.m4a`, `.opus`

Subfolders inside the music directory are scanned automatically.

---

## Discord bot setup

1. Open [https://discord.com/developers/applications](https://discord.com/developers/applications)
2. Create an application and add a **Bot**
3. Copy the bot token into `.env`
4. Enable **Message Content Intent** under Bot settings
5. Invite the bot to your server with permissions to:
   - Read/Send Messages
   - Connect and Speak (voice)

---

## Basic commands

| Command | Description |
|---------|-------------|
| `!join` | Join your voice channel |
| `!play <number or path>` | Play a track |
| `!list` | Show available tracks |
| `!skip` | Skip current track |
| `!stop` | Stop and clear queue |
| `!leave` | Leave voice channel |
| `!volume <0-100>` | Set volume |
| `!play_mode <mode>` | `repeat`, `repeat_playlist`, or `no_repeat` |
| `!help` | Show all commands |

Replace `!` with your prefix if you changed it in `.env`.

---

## Troubleshooting

### `Error: DISCORD_BOT_TOKEN is not set`

Create `.env` from `.env.example` and add your token.

### `ffmpeg` not found / Playing error

FFmpeg is not installed or not in `PATH`. Reinstall FFmpeg and open a new terminal.

### Bot does not respond to commands

- Check that **Message Content Intent** is enabled in the Discord Developer Portal
- Confirm the bot is online and the command prefix matches `.env`

### No music files found

- Check `DISCORD_BOT_MUSIC_SOURCE_FOLDER` in `.env`
- Ensure the path exists and contains supported audio files
- On Linux/macOS, use absolute paths for external drives or NAS mounts

### Cannot connect to voice channel

- You must be in a voice channel when using `!play`
- The bot needs **Connect** and **Speak** permissions

---

## Project structure

```
DiscordOpenMusicBot/
  main.py              # Bot commands and startup
  MusicPlayer.py       # Queue and playback logic
  requirements.txt     # Python dependencies
  .env.example         # Config template
  .env                 # Your local config (not committed to git)
  music/               # Default music folder (optional)
```

## Other languages

- Russian: [README_RU.md](README_RU.md)
