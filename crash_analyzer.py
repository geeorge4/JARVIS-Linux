"""Read recent errors from the local systemd journal."""
import subprocess

COMMANDS = ('проверь сбои linux', 'проверь сбои линукс', 'журнал загрузки',
            'почему компьютер перезагрузился', 'последние сбои')


def recognized(text):
    return text.casefold().replace('ё', 'е').strip(' .!?') in COMMANDS


def collect():
    logs = []
    for boot, label in (('-1', 'Предыдущая загрузка'), ('0', 'Текущая загрузка')):
        result = subprocess.run(
            ['journalctl', '--boot=' + boot, '--priority=err', '--lines=20',
             '--output=short-iso', '--no-pager'],
            capture_output=True, encoding='utf-8', errors='replace', timeout=10,
        )
        if result.returncode:
            logs.append(f'{label}: журнал недоступен.')
        else:
            logs.append(f'{label}:\n{result.stdout.strip()[:6000] or "В доступном журнале ошибок нет."}')
    return '\n\n'.join(logs)


def analyze(jarvis):
    try:
        facts = collect()
    except (OSError, subprocess.TimeoutExpired):
        return 'Не удалось прочитать журнал Linux через journalctl.'
    return facts
