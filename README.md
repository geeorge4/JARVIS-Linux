# JARVIS для Linux

Первый предварительный выпуск JARVIS для Linux. Работает в терминале. Поддерживает локальные заметки, несколько таймеров и текстовый чат через Ollama. Голос, графический интерфейс и игровые интеграции доступны в основной Windows-версии.

[Скачать Linux-версию](https://github.com/geeorge4/JARVIS-Linux/releases) · [Основной проект JARVIS](https://github.com/geeorge4/JARVIS)

## Запуск

Нужен Python 3.10 или новее. Скачай и распакуй `jarvis-linux-0.1.0.tar.gz`, затем выполни в распакованной папке:

```sh
python3 jarvis.py
```

Введи `помощь` для списка команд. Таймеры работают, пока открыт JARVIS. Заметки хранятся в `$XDG_DATA_HOME/jarvis-linux/notes.json` или `~/.local/share/jarvis-linux/notes.json`.

Для чата установи [Ollama для Linux](https://ollama.com/download/linux), запусти его и загрузи модель командой `ollama pull qwen3:4b`. После этого введи в JARVIS `спроси Что такое Linux?`. Для другой модели при запуске укажи `--model ИМЯ`.

## Тесты

```sh
python3 -m unittest discover -s tests -v
```

Код заметок и таймеров перенесён из основного JARVIS. Лицензия MIT.
