"""Interactive JARVIS Linux preview."""
import argparse
import json
from urllib import request

from extra_commands import Extras


from product import VERSION
HELP = """Команды JARVIS
  запиши заметку Купить молоко
  покажи заметки / найди заметку молоко
  поставь таймер на один час и пятнадцать минут
  список таймеров / отмени таймер 1 / отмени таймеры
  спроси Что такое Linux?
  помощь / выход"""


def ask_ollama(prompt, model):
    data = json.dumps({'model': model, 'prompt': prompt, 'stream': False}).encode()
    query = request.Request('http://127.0.0.1:11434/api/generate', data=data,
                            headers={'Content-Type': 'application/json'})
    opener = request.build_opener(request.ProxyHandler({}))
    with opener.open(query, timeout=120) as response:
        result = json.load(response)['response']
    if not isinstance(result, str):
        raise ValueError('Неизвестный формат ответа Ollama.')
    return result.strip()


def main():
    parser = argparse.ArgumentParser(description='JARVIS для Linux')
    parser.add_argument('--version', action='version', version=f'JARVIS Linux {VERSION}')
    parser.add_argument('--model', default='qwen3:4b', help='модель локального Ollama')
    args = parser.parse_args()
    assistant = Extras(lambda text: print(f'\n{text}', flush=True))
    print(f'JARVIS Linux {VERSION}. Введи «помощь» для списка команд.')
    try:
        while True:
            command = input('> ').strip()
            action, _, argument = command.partition(' ')
            if command.lower() == 'выход':
                break
            if command.lower() == 'помощь':
                print(HELP)
                continue
            if action.lower() == 'спроси' and argument.strip():
                try:
                    print(ask_ollama(argument.strip(), args.model))
                except (OSError, ValueError, KeyError, TypeError) as error:
                    print(f'Ошибка Ollama: {error}. Проверь, что Ollama запущен и модель {args.model} загружена.')
                continue
            if command:
                try:
                    print(assistant.handle(command) or 'Неизвестная команда. Введи «помощь».')
                except (OSError, ValueError, ImportError) as error:
                    print(f'Не удалось выполнить команду: {error}')
    except (EOFError, KeyboardInterrupt):
        print()
    finally:
        assistant.close()


if __name__ == '__main__':
    main()
