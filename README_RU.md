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

## Виртуальное окружение (venv)

### Первый запуск: создание окружения

Выполняется один раз в папке проекта:

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

### Следующие запуски: использование существующего окружения

Папка `.venv` остаётся в проекте, создавать её заново не нужно. Достаточно активировать окружение и запустить бота:

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

Можно запустить Python из окружения напрямую, без активации:

```bash
.venv/bin/python main.py          # Linux / macOS
.venv\Scripts\python main.py      # Windows
```

Активация действует только в текущем окне терминала, поэтому в каждом новом терминале окружение нужно активировать снова. Выйти из окружения: `deactivate`.

---

## Проверка и обновление библиотек

Устаревшие библиотеки — частая причина, по которой бот перестаёт работать: Discord меняет протоколы подключения и голосовой связи. Типичные признаки: ошибки подключения к голосовому каналу, бот заходит в канал, но ничего не играет, или ошибки внутри `discord.py`.

Все команды выполняются в активированном окружении `.venv`.

### Проверка

```bash
pip list --outdated                          # пакеты, для которых есть новые версии
pip index versions discord.py                # версии, доступные на PyPI
pip show discord.py python-dotenv PyNaCl     # установленные версии
```

### Обновление

```bash
pip install --upgrade -r requirements.txt    # обновить все пакеты из requirements.txt
pip install --upgrade "discord.py[voice]"    # обновить один пакет ([voice] также ставит PyNaCl)
```

- В `requirements.txt` указаны только минимальные версии (`>=`), поэтому `pip install --upgrade -r requirements.txt` ставит последние версии. Если обновление решило проблему, поднимите минимальную версию в `requirements.txt` до рабочей, чтобы при новой установке не ставилась старая.
- После обновления запустите `python main.py`, проверьте, что в консоли есть строка `Synced N slash commands`, и проверьте `/join` и `/play` в Discord.
- Если окружение сломалось, удалите папку `.venv`, создайте её заново и выполните `pip install -r requirements.txt`.

### Обновление FFmpeg

FFmpeg не устанавливается через pip, его обновляют системным менеджером пакетов:

| ОС | Команда |
|----|---------|
| Fedora / RHEL | `sudo dnf upgrade ffmpeg` |
| Debian / Ubuntu | `sudo apt update && sudo apt upgrade ffmpeg` |
| Arch | `sudo pacman -Syu ffmpeg` |
| macOS | `brew upgrade ffmpeg` |
| Windows | `winget upgrade Gyan.FFmpeg` |

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
| `DISCORD_BOT_BITRATE` | Битрейт звука, отправляемого в Discord, в кбит/с. По умолчанию `96`. Другие варианты: `128` (выше качество, больше трафика), `64` (меньше трафика, ниже качество) | `DISCORD_BOT_BITRATE=96` |
| `DISCORD_BOT_DEBUG` | Выводить в консоль все сообщения из чатов, которые видит бот (по умолчанию выключено) | `DISCORD_BOT_DEBUG=true` |

**Важно:**
- Не коммитьте `.env` в git (там секретный токен)
- Не публикуйте токен в открытом доступе
- Для внешних дисков и NAS используйте абсолютные пути
- Если переменная не задана, используются значения по умолчанию: префикс `/`, папка `music`

Поддерживаемые форматы: `.mp3`, `.wav`, `.ogg`, `.flac`, `.m4a`, `.opus`

Подпапки внутри музыкальной директории сканируются автоматически.

---

## Настройка Discord-бота (Developer Portal)

В этом разделе описано, как создать и настроить бота на [Discord Developer Portal](https://discord.com/developers/applications) и добавить его на сервер.

### 1. Создание приложения

1. Откройте [https://discord.com/developers/applications](https://discord.com/developers/applications)
2. Войдите в аккаунт Discord
3. Нажмите **New Application** (Новое приложение)
4. Введите имя (например, `Music Bot`) и нажмите **Create** (Создать)

Вы попадёте на страницу настроек приложения. Код бота читает параметры из локального файла `.env`; портал нужен только для создания учётной записи бота и получения токена.

### 2. Создание бота и копирование токена

1. В левом меню откройте **Bot** (Бот)
2. Нажмите **Add Bot** → **Yes, do it!**
3. В блоке **Token** (Токен) нажмите **Reset Token** или **View Token**
4. Скопируйте токен и вставьте в `.env`:

```env
DISCORD_BOT_TOKEN=вставьте_токен_сюда
```

**Важно:**
- Не публикуйте токен и не коммитьте его в git
- Если токен утёк — сразу нажмите **Reset Token** на портале и обновите `.env`

Дополнительно на странице **Bot**:
- **Username** — имя бота в Discord
- **Icon** — аватар
- **Public Bot** — можно оставить включённым, если не нужно ограничивать приглашения

### 3. Включение Privileged Gateway Intents

На той же странице **Bot** прокрутите до **Privileged Gateway Intents** и включите:

| Intent | Нужен | Зачем |
|--------|-------|-------|
| **Message Content Intent** | Да | Префикс-команды (`!play` и т.д.) — бот должен читать текст сообщений |
| **Server Members Intent** | Нет | Ботом не используется, можно не включать |

Нажмите **Save Changes** (Сохранить изменения) внизу страницы.

Без **Message Content Intent** бот запустится, но не будет отвечать на команды с префиксом.

### 4. Добавление бота на сервер

1. В левом меню откройте **OAuth2** → **URL Generator**
2. В **Scopes** (Области) включите:
   - **bot**
   - **applications.commands** (нужно для `/play`, `/list` и других slash-команд с подсказками при вводе)
3. В **Bot Permissions** (Права бота) включите минимум:

| Право | Зачем |
|-------|-------|
| Read Messages / View Channels | Видеть текстовые каналы |
| Send Messages | Отвечать на команды |
| Read Message History | Читать сообщения с командами |
| Connect | Подключаться к голосовым каналам |
| Speak | Воспроизводить звук |
| Use Voice Activity | Голосовое подключение (рекомендуется) |

4. Скопируйте сгенерированный **URL** внизу страницы
5. Откройте ссылку в браузере
6. Выберите сервер, где у вас есть право **Управление сервером** (Manage Server)
7. Нажмите **Authorize** (Авторизовать) и пройдите проверку

Бот появится в списке участников (офлайн, пока вы не запустите `python main.py`).

**Если нет slash-команд:** сгенерируйте новую ссылку с включённым **applications.commands** и откройте её снова (можно пригласить того же бота повторно — права обновятся).

### 5. Локальная настройка (`.env`)

После добавления токена в `.env` укажите префикс команд и папку с музыкой (см. [Настройка (.env)](#настройка-env) выше):

```env
DISCORD_BOT_TOKEN=your_token_here
DISCORD_BOT_PREFIX=!
DISCORD_BOT_MUSIC_SOURCE_FOLDER=music
```

`DISCORD_BOT_PREFIX` можно изменить на любой префикс (например `?` или `music.`). После изменения `.env` перезапустите бота.

### 6. Запуск и проверка

```bash
python main.py
```

При запуске в консоли должно появиться:
- `Bot ... started. Id: ...`
- `Synced N slash commands` — slash-команды зарегистрированы в Discord

В Discord:
- Команды с префиксом: например `!help` или `!list` (или ваш префикс из `.env`)
- Slash-команды (подсказки при вводе): наберите `/`, выберите бота, затем `/play`, `/join` и т.д.

---

## Основные команды

Доступны **оба** способа: команды с префиксом и slash-команды. Префикс задаётся в `DISCORD_BOT_PREFIX` в `.env` (по умолчанию `/`). Slash-команды всегда начинаются с `/`.

| Пример с префиксом | Slash-команда | Описание |
|--------------------|---------------|----------|
| `!join` | `/join` | Подключиться к вашему голосовому каналу |
| `!play <номер или имя>` | `/play` | Воспроизвести трек (в `/play` есть подсказки при вводе) |
| `!list` | `/list` | Показать доступные треки |
| `!rescan` | `/rescan` | Пересканировать папку с музыкой после добавления или удаления файлов |
| `!skip` | `/skip` | Пропустить текущий трек |
| `!stop` | `/stop` | Остановить и очистить очередь |
| `!leave` | `/leave` | Выйти из голосового канала |
| `!volume <0-100>` | `/volume` | Показать или установить громкость |
| `!play_mode <режим>` | `/play_mode` | `repeat`, `repeat_playlist` или `no_repeat` (в slash — выпадающий список) |
| `!help` | — | Показать все команды с префиксом |
| `!ping` | `/ping` | Проверить, что бот онлайн |

В примерах используется префикс `!`. По умолчанию префикс `/`; замените `!` на префикс из вашего `.env`. Префикс, отличный от `/` (например `!`), проще отличить от slash-команд.

**Как использовать `/play`:** наберите `/`, выберите бота, команду **play**, затем номер или имя трека из `/list`.

**Как использовать play с префиксом:**

```
!list                          сначала посмотреть список
!play 3                        воспроизвести по номеру
!play song.mp3                 поиск по части имени файла
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

### Slash-команды (`/play`) не появляются

- Пригласите бота заново со scope **applications.commands** (OAuth2 → URL Generator)
- Перезапустите бота и подождите несколько минут — Discord синхронизирует команды
- В консоли при запуске должно быть `Synced N slash commands`

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
  main.py              # Запуск бота: создание бота, загрузка cogs, лог запуска
  config.py            # Настройки из .env
  library.py           # Сканирование папки с музыкой, кэш и поиск треков
  views.py             # Страницы /list с кнопками Previous/Next
  MusicPlayer.py       # Очередь и режимы повтора для одного сервера
  cogs/
    music.py           # Музыкальные команды и воспроизведение
    utility.py         # ping, info, debug, channels
  requirements.txt     # Python-зависимости
  .env.example         # Шаблон конфигурации
  .env                 # Ваша локальная конфигурация (не коммитится в git)
  music/               # Папка с музыкой по умолчанию (опционально)
```

## Другие языки

- English: [README.md](README.md)
