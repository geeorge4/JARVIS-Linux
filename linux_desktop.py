"""Linux desktop and XDG paths used by JARVIS."""
import os
from pathlib import Path
import shutil
import subprocess


DATA_HOME = Path(os.environ.get('XDG_DATA_HOME') or Path.home() / '.local/share')
DATA_DIR = DATA_HOME / 'jarvis-linux'
ROOT = Path(__file__).resolve().parent
WAYLAND = os.environ.get('XDG_SESSION_TYPE') == 'wayland' or bool(os.environ.get('WAYLAND_DISPLAY'))


def launch(*commands):
    for command in commands:
        executable = shutil.which(command[0])
        if executable:
            subprocess.Popen([executable, *command[1:]], start_new_session=True)
            return
    raise OSError('Не найдено: ' + ', '.join(command[0] for command in commands))


def open_target(target):
    launch(('xdg-open', str(target)), ('gio', 'open', str(target)))


def user_folder(name):
    if shutil.which('xdg-user-dir'):
        result = subprocess.run(['xdg-user-dir', name.upper()], capture_output=True, text=True, timeout=3)
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip())
    return Path.home() / name


def settings():
    launch(('gnome-control-center',), ('systemsettings',), ('xfce4-settings-manager',),
           ('cinnamon-settings',), ('mate-control-center',), ('lxqt-config',))


def screenshot(path):
    path = Path(path)
    if WAYLAND:
        for command in (
            ('grim', str(path)),
            ('spectacle', '-b', '-n', '-o', str(path)),
            ('gnome-screenshot', '-f', str(path)),
        ):
            if shutil.which(command[0]):
                try:
                    completed = subprocess.run(command, capture_output=True, timeout=12)
                except subprocess.TimeoutExpired:
                    continue
                if completed.returncode == 0 and path.is_file() and path.stat().st_size:
                    return
        raise OSError('Композитор Wayland не предоставил снимок экрана.')
    from PIL import ImageGrab
    with ImageGrab.grab() as image:
        image.save(path)
