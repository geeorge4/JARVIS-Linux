# JARVIS для Linux

Голосовой помощник и игровой напарник. Порт включает интерфейс со сферой, нейрочат, рабочий стол, мини-оверлей, трей, быстрые сценарии, локальные заметки и таймеры. Терминальный режим также доступен.

[Скачать Linux-версию](https://github.com/geeorge4/JARVIS-Linux/releases) · [Основной проект JARVIS](https://github.com/geeorge4/JARVIS) · [Команды](COMMANDS.md)

## Установка и запуск

Нужны Python 3.10+ и графический сеанс для интерфейса. На Ubuntu/Debian сначала установи системные зависимости:

```sh
sudo apt install python3-tk python3-venv libportaudio2 xdg-utils libglib2.0-bin
```

Скачай `jarvis-linux-0.2.0.tar.gz`, распакуй архив и выполни в распакованной папке:

```sh
sh install.sh
sh start.sh
```

При первом запуске для полного режима GUI подходит демонстрационный ключ `activation-1`. Заметки, настройки, история и игровая статистика находятся в `$XDG_DATA_HOME/jarvis-linux` или `~/.local/share/jarvis-linux`. При обновлении ставь новую версию в отдельную папку и перенеси туда свои `round-drops`, `speech-models` и файлы XTTS. Данные из XDG приложение подхватит автоматически.

Команда `python3 jarvis.py` запускает прежний терминальный режим. В нём чат использует обычный адрес Ollama `127.0.0.1:11434`.

## Голос и локальный ИИ

- Whisper Base распознаёт запросы, Whisper Tiny слушает слово «Джарвис», Piper озвучивает ответы. Для загрузки моделей выполни `.venv/bin/python installer/prepare_models.py`.
- Для GUI установи [Ollama](https://ollama.com/download/linux), затем выполни `.venv/bin/python installer/prepare_models.py --qwen`. Это загрузит Qwen в папку данных JARVIS. GUI запускает отдельный сервер на `127.0.0.1:11435`.
- XTTS использует отдельное окружение `xtts-runtime` и файлы `xtts-model` и `xtts-reference.wav` в папке приложения. Установи зависимости из `requirements-xtts.txt` в это окружение и используй голосовой образец с разрешением владельца.

## Рабочий стол и игры

- **Приложения и мультимедиа.** Поиск индексирует записи XDG. Для громкости используется `wpctl` или `pactl`, для управления плеером нужен `playerctl`. Окно «Выполнить» доступно через Ctrl+Shift+R, мини-оверлей через Ctrl+Shift+O. На X11 сочетания глобальные с pynput. На Wayland они работают внутри окна. Трей зависит от окружения рабочего стола и поддержки AppIndicator.
- **Снимки и OCR.** Для распознавания установи `tesseract-ocr`, `tesseract-ocr-rus` и `tesseract-ocr-eng`. Захват на Wayland зависит от композитора и доступности `grim`, `spectacle` или `gnome-screenshot`. Сбои читаются из доступных журналов `journalctl`.
- **CS2.** Раскидки, тренировка, игровой журнал и панель сессии доступны в GUI. Для событий создай конфиг командой `.venv/bin/python -c 'from cs2_ace import config, token; print(config(token()))'` и сохрани его как `game/csgo/cfg/gamestate_integration_jarvis.cfg` в папке игры. Для гимнов добавь свои WAV в `round-drops`. Поддерживаются `paplay`, `pw-play` или `aplay`. Правила именования описаны в [основном проекте](https://github.com/geeorge4/JARVIS#counter-strike-2).
- **Наблюдение.** Панель сессии принимает обновляемый CSV с колонкой `fps` или временем кадра в миллисекундах. Guardian использует доступные датчики. War Thunder считывает экспериментальные события через `localhost:8111`.

GitHub Actions проверяет запуск GUI в X11 через Xvfb и запускает автоматические тесты на Ubuntu. Работа с реальным микрофоном, некоторыми композиторами Wayland и событиями в живом матче зависит от конфигурации и требует проверки на месте.

Лицензия MIT. Условия сторонних компонентов перечислены в [NOTICE.md](NOTICE.md).
