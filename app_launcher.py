"""Поиск и запуск установленных приложений через XDG."""
import configparser
import os
import re
from pathlib import Path
from linux_desktop import DATA_HOME, launch

ALIASES = {'телеграм': 'telegram', 'телеграмм': 'telegram', 'дискорд': 'discord',
           'стим': 'steam', 'стима': 'steam', 'хром': 'google chrome',
           'гугл хром': 'google chrome', 'вс код': 'visual studio code',
           'роблокс': 'roblox', 'ноушен': 'notion', 'спотифай': 'spotify'}

class Launcher:
    def __init__(self):
        self.apps = None

    def refresh(self, update=False):
        self.apps = {}
        directories = (os.environ.get('XDG_DATA_DIRS') or '/usr/local/share:/usr/share').split(':')
        seen = set()
        for directory in [DATA_HOME, *(Path(item) for item in directories if item)]:
            apps = directory / 'applications'
            for path in sorted(apps.rglob('*.desktop')):
                desktop_id = '-'.join(path.relative_to(apps).parts)
                if desktop_id in seen:
                    continue
                seen.add(desktop_id)
                entry = configparser.ConfigParser(interpolation=None, strict=False)
                try:
                    entry.read(path, encoding='utf-8')
                    app = entry['Desktop Entry']
                    if app.get('Type') != 'Application' or app.getboolean('Hidden', False) or app.getboolean('NoDisplay', False):
                        continue
                    name = app.get('Name', '').strip().lower()
                except (configparser.Error, UnicodeError, KeyError, ValueError):
                    continue
                if name:
                    self.apps.setdefault(name, path)
        return len(self.apps)

    @staticmethod
    def target(text):
        text = text.lower().replace('ё','е').strip(' .,!?')
        match = re.search(r'(?:откро[йи]|открыть|открывай|запусти(?:ть)?|включи(?:ть)?|open|launch|start)\s+(.+)', text)
        if not match: return None
        name = re.sub(r'\b(?:пожалуйста|мне|приложение|программу|сейчас)\b', '', match.group(1))
        name = re.sub(r'\s+',' ',name).strip(' .,!?')
        return ALIASES.get(name,name)

    def find(self, name):
        if self.apps is None: self.refresh()
        name = ALIASES.get(name.lower(),name.lower())
        if name in self.apps: return name, []
        matches = [n for n in self.apps if name and name in n]
        if len(matches)==1: return matches[0], []
        if matches: return None, sorted(matches)[:6]
        import difflib
        return None, difflib.get_close_matches(name,list(self.apps),n=4,cutoff=.55)

    def open(self, name):
        selected, suggestions = self.find(name)
        if not selected:
            return ('Нашёл несколько вариантов: ' if suggestions else 'Приложение не найдено: ') + (', '.join(suggestions) if suggestions else name) + '. Уточни название.'
        launch(('gio', 'launch', str(self.apps[selected])))
        return 'Отправил команду открыть ' + selected + '.'
