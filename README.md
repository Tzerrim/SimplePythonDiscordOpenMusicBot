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

## Virtual environment (venv)

### First run: create the environment

Run once from the project folder:

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Windows:**

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Next runs: reuse the existing environment

The `.venv` folder stays in the project, so don't create it again. Activate it and start the bot:

**Linux / macOS:**

```bash
source .venv/bin/activate
python main.py
```

**Windows:**

```bat
.venv\Scripts\activate
python main.py
```

You can also run the environment's Python directly, without activating it:

```bash
.venv/bin/python main.py          # Linux / macOS
.venv\Scripts\python main.py      # Windows
```

Activation applies only to the current terminal window, so activate the environment again in each new terminal. To leave it, run `deactivate`.

---

## Checking and updating libraries

Outdated libraries are a common reason the bot stops working, because Discord changes its connection and voice protocols. Typical signs are voice connection errors, the bot joining a channel but playing nothing, or errors from inside `discord.py`.

Run all commands inside the activated `.venv`.

### Check

```bash
pip list --outdated                          # packages with newer versions available
pip index versions discord.py                # versions available on PyPI
pip show discord.py python-dotenv PyNaCl     # installed versions
```

### Update

```bash
pip install --upgrade -r requirements.txt    # upgrade all packages in requirements.txt
pip install --upgrade "discord.py[voice]"    # upgrade one package ([voice] also installs PyNaCl)
```

- `requirements.txt` only sets minimum versions (`>=`), so `pip install --upgrade -r requirements.txt` installs the latest releases. If an upgrade fixes a problem, raise the minimum version in `requirements.txt` to the working one so new installs don't get an older version.
- After upgrading, run `python main.py`, check that the console shows `Synced N slash commands`, and test `/join` and `/play` in Discord.
- If the environment is broken, delete the `.venv` folder, create it again, and run `pip install -r requirements.txt`.

### Updating FFmpeg

FFmpeg is not installed through pip. Update it with your system package manager:

| OS | Command |
|----|---------|
| Fedora / RHEL | `sudo dnf upgrade ffmpeg` |
| Debian / Ubuntu | `sudo apt update && sudo apt upgrade ffmpeg` |
| Arch | `sudo pacman -Syu ffmpeg` |
| macOS | `brew upgrade ffmpeg` |
| Windows | `winget upgrade Gyan.FFmpeg` |

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
| `DISCORD_BOT_DEBUG` | Print every chat message the bot sees to the console (off by default) | `DISCORD_BOT_DEBUG=true` |

**Important:**
- Do not commit `.env` to git (it contains your secret token)
- Do not share your token publicly
- Use absolute paths for external drives and NAS mounts
- If a variable is missing, the bot uses defaults: prefix `/`, folder `music`

Supported audio formats: `.mp3`, `.wav`, `.ogg`, `.flac`, `.m4a`, `.opus`

Subfolders inside the music directory are scanned automatically.

---

## Discord bot setup (Developer Portal)

This section explains how to create and configure the bot on the [Discord Developer Portal](https://discord.com/developers/applications) and add it to your server.

### 1. Create an application

1. Open [https://discord.com/developers/applications](https://discord.com/developers/applications)
2. Log in with your Discord account
3. Click **New Application**
4. Enter a name (for example `Music Bot`) and click **Create**

You are now on the application settings page. The bot code reads settings from your local `.env` file; the portal is only for creating the bot account and getting the token.

### 2. Create the bot and copy the token

1. In the left sidebar, open **Bot**
2. Click **Add Bot** → **Yes, do it!**
3. Under **Token**, click **Reset Token** (or **View Token** if this is a new bot)
4. Copy the token and paste it into `.env`:

```env
DISCORD_BOT_TOKEN=paste_your_token_here
```

**Important:**
- Never share your token publicly or commit it to git
- If the token leaks, click **Reset Token** in the portal immediately and update `.env`

Optional on the **Bot** page:
- **Username** — change how the bot appears in Discord
- **Icon** — upload an avatar
- **Public Bot** — leave enabled unless you want to restrict who can invite it

### 3. Enable required Privileged Gateway Intents

Still on the **Bot** page, scroll to **Privileged Gateway Intents** and enable:

| Intent | Required | Why |
|--------|----------|-----|
| **Message Content Intent** | Yes | Prefix commands (`!play`, etc.) need to read message text |
| **Server Members Intent** | No | Not used by the bot, can stay off |

Click **Save Changes** at the bottom of the page.

Without **Message Content Intent**, the bot will start but will not respond to prefix commands.

### 4. Invite the bot to your server

1. In the left sidebar, open **OAuth2** → **URL Generator**
2. Under **Scopes**, enable:
   - **bot**
   - **applications.commands** (required for `/play`, `/list`, and other slash commands with typing hints)
3. Under **Bot Permissions**, enable at least:

| Permission | Why |
|------------|-----|
| Read Messages / View Channels | See text channels |
| Send Messages | Reply to commands |
| Read Message History | Read command messages |
| Connect | Join voice channels |
| Speak | Play audio |
| Use Voice Activity | Voice connection (recommended) |

4. Copy the generated **URL** at the bottom
5. Open the URL in your browser
6. Select the server where you have **Manage Server** permission
7. Click **Authorize** and complete the captcha

The bot should appear in your server member list (offline until you run `python main.py`).

**Re-invite if slash commands are missing:** If `/play` does not appear in Discord, generate a new invite URL with **applications.commands** checked and open it again (you can invite the same bot twice — permissions will update).

### 5. Configure local settings (`.env`)

After the token is in `.env`, set your command prefix and music folder (see [Configuration (.env)](#configuration-env) above):

```env
DISCORD_BOT_TOKEN=your_token_here
DISCORD_BOT_PREFIX=!
DISCORD_BOT_MUSIC_SOURCE_FOLDER=music
```

Change `DISCORD_BOT_PREFIX` to any prefix you like (for example `?` or `music.`). Restart the bot after changing `.env`.

### 6. Start the bot and verify

```bash
python main.py
```

On startup you should see:
- `Bot ... started. Id: ...`
- `Synced N slash commands` — slash commands registered with Discord

In Discord:
- Prefix commands: type your prefix, for example `!help` or `!list`
- Slash commands (typing hints): type `/` and select your bot, then choose `/play`, `/join`, etc.

---

## Basic commands

You can use **both** prefix commands and slash commands. Prefix uses the value from `DISCORD_BOT_PREFIX` in `.env` (default `/`). Slash commands always start with `/`.

| Prefix example | Slash command | Description |
|----------------|---------------|-------------|
| `!join` | `/join` | Join your voice channel |
| `!play <number or name>` | `/play` | Play a track (`/play` suggests tracks while typing) |
| `!list` | `/list` | Show available tracks |
| `!rescan` | `/rescan` | Rescan the music folder after adding or removing files |
| `!skip` | `/skip` | Skip current track |
| `!stop` | `/stop` | Stop and clear queue |
| `!leave` | `/leave` | Leave voice channel |
| `!volume <0-100>` | `/volume` | Show or set volume |
| `!play_mode <mode>` | `/play_mode` | `repeat`, `repeat_playlist`, or `no_repeat` (dropdown on slash) |
| `!help` | — | Show all prefix commands |
| `!ping` | `/ping` | Check if the bot is online |

The examples use `!` as the prefix. The default prefix is `/`; replace `!` with the prefix from your `.env`. A prefix other than `/` (for example `!`) is easier to tell apart from slash commands.

**Using `/play`:** type `/`, select the bot, choose **play**, then pick or type a track number from `/list`.

**Using prefix play:**

```
!list                          show track list first
!play 3                        play by number
!play song.mp3                 search by part of the filename
```

---

## Troubleshooting

### `Error: DISCORD_BOT_TOKEN is not set`

Create `.env` from `.env.example` and add your token.

### `ffmpeg` not found / Playing error

FFmpeg is not installed or not in `PATH`. Reinstall FFmpeg and open a new terminal.

### Bot does not respond to commands

- Check that **Message Content Intent** is enabled in the Discord Developer Portal
- Confirm the bot is online and the command prefix matches `.env`

### Slash commands (`/play`) do not appear

- Re-invite the bot with the **applications.commands** scope (OAuth2 → URL Generator)
- Restart the bot and wait a few minutes for Discord to sync commands globally
- Make sure the console shows `Synced N slash commands` on startup

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
