# Discord Open Music Bot

Discord-бот для воспроизведения локальных музыкальных файлов из папки (включая подпапки).

## Требования

| Компонент | Версия |
|-----------|--------|
| Python | 3.11 или новее |
| FFmpeg | 4.x или новее (рекомендуется 8.x) |
| Интернет | Нужен для подключения к Discord |
| Токен Discord-бота | Обязателен |

### Python-пакеты (устанавливаются через pip)

- `discord.py[voice]` — Discord API и голосовой канал
- `python-dotenv` — загрузка настроек из `.env`

Они перечислены в файле `requirements.txt`.

### Системная зависимость (не устанавливается через pip)

- **FFmpeg** — нужен для воспроизведения аудио. Устанавливается отдельно и должен быть доступен в `PATH`.

---

## Windows

### 1. Установка Python

1. Скачайте Python с [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Запустите установщик
3. Включите **"Add python.exe to PATH"**
4. Проверьте в командной строке или PowerShell:

```bat
python --version
pip --version
```

### 2. Установка FFmpeg

**Вариант A — winget (рекомендуется):**

```bat
winget install Gyan.FFmpeg
```

**Вариант B — Chocolatey:**

```bat
choco install ffmpeg
```

**Вариант C — вручную:**

1. Скачайте сборку с [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)
2. Распакуйте архив
3. Добавьте папку `bin` в системную переменную `PATH`

Проверка:

```bat
ffmpeg -version
```

### 3. Установка и запуск бота

```bat
cd path\to\DiscordOpenMusicBot
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Отредактируйте `.env` и укажите токен Discord-бота и путь к папке с музыкой.

```bat
python main.py
```

---

## Linux

### 1. Установка Python

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

Проверка:

```bash
python3 --version
pip3 --version
```

### 2. Установка FFmpeg

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

Проверка:

```bash
ffmpeg -version
```

### 3. Установка и запуск бота

```bash
cd /path/to/DiscordOpenMusicBot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Отредактируйте `.env` и укажите токен Discord-бота и путь к папке с музыкой.

```bash
python main.py
```

### Опционально: запуск как фоновый сервис (systemd)

Создайте файл `/etc/systemd/system/discord-music-bot.service`:

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

Включите и запустите:

```bash
sudo systemctl daemon-reload
sudo systemctl enable discord-music-bot
sudo systemctl start discord-music-bot
```

---

## macOS

### 1. Установка Homebrew (если ещё не установлен)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Установка Python и FFmpeg

```bash
brew install python ffmpeg
```

Проверка:

```bash
python3 --version
ffmpeg -version
```

### 3. Установка и запуск бота

```bash
cd /path/to/DiscordOpenMusicBot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Отредактируйте `.env` и укажите токен Discord-бота и путь к папке с музыкой.

```bash
python main.py
```

---

## Настройка (.env)

Скопируйте пример и отредактируйте:

| ОС | Команда |
|----|---------|
| Windows | `copy .env.example .env` |
| Linux / macOS | `cp .env.example .env` |

### Пример файла `.env`

Создайте файл `.env` в корне проекта. Он должен выглядеть так:

```env
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_BOT_PREFIX=!
DISCORD_BOT_MUSIC_SOURCE_FOLDER=music
```

**Минимальный пример (локальная папка `music` в проекте):**

```env
DISCORD_BOT_TOKEN=MTIzNDU2Nzg5MDEyMzQ1Njc4.GAbCdE.fGhIjKlMnOpQrStUvWxYzAbCdEfGhIj
DISCORD_BOT_PREFIX=!
DISCORD_BOT_MUSIC_SOURCE_FOLDER=music
```

**Пример для Windows (своя папка с музыкой):**

```env
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_BOT_PREFIX=!
DISCORD_BOT_MUSIC_SOURCE_FOLDER=D:\Music\MyPlaylist
```

**Пример для Linux / macOS (абсолютный путь):**

```env
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_BOT_PREFIX=!
DISCORD_BOT_MUSIC_SOURCE_FOLDER=/home/user/Music
```

**Пример для NAS / сетевого хранилища:**

```env
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_BOT_PREFIX=!
DISCORD_BOT_MUSIC_SOURCE_FOLDER=/mnt/nas/Music/Library
```

### Описание переменных

| Переменная | Описание | Пример |
|------------|----------|--------|
| `DISCORD_BOT_TOKEN` | Токен бота из Discord Developer Portal | `DISCORD_BOT_TOKEN=your_token_here` |
| `DISCORD_BOT_PREFIX` | Префикс команд | `!` |
| `DISCORD_BOT_MUSIC_SOURCE_FOLDER` | Путь к папке с музыкой | `music` или `D:\Music` или `/home/user/Music` |

**Важно:**
- Не коммитьте `.env` в git (там секретный токен)
- Не публикуйте токен в открытом доступе
- Для внешних дисков и NAS используйте абсолютные пути
- Если переменная не задана, используются значения по умолчанию: префикс `!`, папка `music`

Поддерживаемые форматы: `.mp3`, `.wav`, `.ogg`, `.flac`, `.m4a`, `.opus`

Подпапки внутри музыкальной директории сканируются автоматически.

---

## Настройка Discord-бота

1. Откройте [https://discord.com/developers/applications](https://discord.com/developers/applications)
2. Создайте приложение и добавьте **Bot**
3. Скопируйте токен бота в `.env`
4. Включите **Message Content Intent** в настройках бота
5. Пригласите бота на сервер с правами:
   - Читать/отправлять сообщения
   - Подключаться и говорить (голосовой канал)

---

## Основные команды

| Команда | Описание |
|---------|----------|
| `!join` | Подключиться к вашему голосовому каналу |
| `!play <номер или путь>` | Воспроизвести трек |
| `!list` | Показать доступные треки |
| `!skip` | Пропустить текущий трек |
| `!stop` | Остановить и очистить очередь |
| `!leave` | Выйти из голосового канала |
| `!volume <0-100>` | Установить громкость |
| `!play_mode <режим>` | `repeat`, `repeat_playlist` или `no_repeat` |
| `!help` | Показать все команды |

Замените `!` на свой префикс, если вы изменили его в `.env`.

### Как использовать `!play`

```
!list                          сначала посмотреть список
!play 3                        воспроизвести по номеру
!play album/song.mp3           воспроизвести по пути к файлу
!play song.mp3                 поиск по части имени
```

---

## Решение проблем

### `Error: DISCORD_BOT_TOKEN is not set`

Создайте `.env` из `.env.example` и добавьте токен.

### `ffmpeg` not found / Playing error

FFmpeg не установлен или не добавлен в `PATH`. Переустановите FFmpeg и откройте новый терминал.

### Бот не отвечает на команды

- Проверьте, что **Message Content Intent** включён в Discord Developer Portal
- Убедитесь, что бот онлайн и префикс команд совпадает с `.env`

### Музыкальные файлы не найдены

- Проверьте `DISCORD_BOT_MUSIC_SOURCE_FOLDER` в `.env`
- Убедитесь, что путь существует и содержит поддерживаемые аудиофайлы
- На Linux/macOS для внешних дисков и NAS используйте абсолютные пути

### Не удаётся подключиться к голосовому каналу

- Вы должны находиться в голосовом канале при использовании `!play`
- Боту нужны права **Connect** и **Speak**

---

## Структура проекта

```
DiscordOpenMusicBot/
  main.py              # Команды бота и запуск
  MusicPlayer.py       # Очередь и логика воспроизведения
  requirements.txt     # Python-зависимости
  .env.example         # Шаблон конфигурации
  .env                 # Ваша локальная конфигурация (не коммитится в git)
  music/               # Папка с музыкой по умолчанию (опционально)
```

## Другие языки

- English: [README.md](README.md)
