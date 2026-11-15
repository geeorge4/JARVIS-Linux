"""Portable notes and timer commands from JARVIS."""
import math
import re
import threading
import time

def norm(text):return re.sub(r'\s+',' ',text.lower().replace('ё','е')).strip(' .!?')

TIMER_PART = re.compile(r'(\d+)\s*(секунд[аыу]?|сек|минут[ауы]?|мин|час(?:а|ов)?)')
TIMER_UNITS = {'с': 1, 'м': 60, 'ч': 3600}
TIMER_NUMBERS = {
    'один': '1', 'одну': '1', 'одна': '1', 'два': '2', 'две': '2',
    'три': '3', 'четыре': '4', 'пять': '5', 'шесть': '6', 'семь': '7',
    'восемь': '8', 'девять': '9', 'десять': '10', 'пятнадцать': '15', 'тридцать': '30',
}
TIMER_NUMBER_WORD = re.compile(r'\b(?:' + '|'.join(TIMER_NUMBERS) + r')\b')

class Extras:
    def __init__(self, notify, note_store):
        self.notify = notify
        self.timers = {}
        self.lock = threading.Lock()
        self.next_id = 1
        self.note_store = note_store

    def notes(self):
        return self.note_store.list()

    def recognized(self,text):
        s=norm(text)
        return (s in ('покажи заметки', 'список таймеров', 'отмени таймеры') or
                s.startswith(('запиши заметку ', 'найди заметку ', 'поставь таймер ',
                              'таймер ', 'отмени таймер ')))

    def handle(self,text):
        s=norm(text)
        if s.startswith('запиши заметку '):
            value=text.strip().split(maxsplit=2)[2]
            if not value:return 'Продиктуй текст заметки.'
            self.note_store.add(value)
            return 'Заметка записана.'
        if s=='покажи заметки' or s.startswith('найди заметку '):
            notes=self.notes();query=s[len('найди заметку '):] if s.startswith('найди заметку ') else ''
            matches=[n for n in notes if isinstance(n,dict) and query in norm(str(n.get('text','')))][-10:]
            return '\n'.join(f"{i+1}. {n['text']}" for i,n in enumerate(matches)) or 'Заметки не найдены.'
        if s.startswith(('таймер ','поставь таймер ')):
            s = TIMER_NUMBER_WORD.sub(lambda match: TIMER_NUMBERS[match[0]], s)
            duration = re.sub(r'^(?:поставь )?таймер (?:на )?', '', s)
            if not re.fullmatch(rf'{TIMER_PART.pattern}(?:(?: и | ){TIMER_PART.pattern}){{0,2}}', duration):
                return 'Пример: таймер 30 секунд или таймер 1 час 15 минут.'
            parts = TIMER_PART.findall(duration)
            if len({unit[0] for _, unit in parts}) != len(parts):
                return 'Укажи часы, минуты и секунды по одному разу.'
            parts = [(amount.lstrip('0') or '0', unit) for amount, unit in parts]
            if any(len(amount) > 5 for amount, _ in parts):
                return 'Таймер можно поставить от 1 секунды до 24 часов.'
            seconds = sum(int(amount) * TIMER_UNITS[unit[0]] for amount, unit in parts)
            if not 1<=seconds<=86400:return 'Таймер можно поставить от 1 секунды до 24 часов.'
            label = ' '.join(f'{int(amount)} {unit}' for amount, unit in parts)
            with self.lock:
                if len(self.timers)>=20:return 'Уже работают 20 таймеров.'
                identifier=self.next_id;self.next_id+=1
                def done():
                    with self.lock:
                        if identifier not in self.timers:return
                        self.timers.pop(identifier)
                    self.notify(f'Таймер {identifier} завершён: {label}.')
                timer=threading.Timer(seconds,done);timer.daemon=True;self.timers[identifier]=(timer,time.monotonic()+seconds);timer.start()
            return f'Таймер {identifier} поставлен на {label}.'
        if s=='список таймеров':
            with self.lock:return '\n'.join(f'{i}: осталось {max(0,int(end-time.monotonic()))} сек.' for i,(_,end) in self.timers.items()) or 'Активных таймеров нет.'
        if s=='отмени таймеры':self.close();return 'Все таймеры отменены.'
        if s.startswith('отмени таймер '):
            s = TIMER_NUMBER_WORD.sub(lambda match: TIMER_NUMBERS[match[0]], s)
            number = re.fullmatch(r'отмени таймер (?:номер )?([0-9]{1,18})', s)
            if number is None:
                return 'Укажи номер из списка таймеров. Например: отмени таймер 2.'
            identifier = int(number.group(1))
            if self.cancel_timer(identifier):
                return f'Таймер {identifier} отменён.'
            return f'Активного таймера {identifier} нет.'
        return None

    def close(self):
        with self.lock:
            for timer,_ in self.timers.values():timer.cancel()
            self.timers.clear()

    def timer_snapshot(self):
        with self.lock:
            now=time.monotonic()
            return [(identifier,max(0,math.ceil(end-now))) for identifier,(_,end) in self.timers.items()]

    def cancel_timer(self, identifier):
        with self.lock:
            entry=self.timers.pop(identifier,None)
            if entry is None:return False
            entry[0].cancel()
            return True

