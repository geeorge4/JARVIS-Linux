"""Playback for the user's optional round clips."""
import shutil
import subprocess
import threading
import warnings

_lock = threading.Lock()
_player = None
SND_FILENAME = SND_ASYNC = SND_NODEFAULT = 0


def PlaySound(path, flags=0):
    global _player
    with _lock:
        if _player is not None and _player.poll() is None:
            _player.terminate()
            try:
                _player.wait(timeout=1)
            except subprocess.TimeoutExpired:
                _player.kill()
                _player.wait()
        _player = None
        if path is None:
            return
        for binary, args in (('paplay', []), ('pw-play', []), ('aplay', ['-q'])):
            if executable := shutil.which(binary):
                _player = subprocess.Popen([executable, *args, str(path)],
                                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
        warnings.warn('Для гимнов установи paplay, pw-play или aplay.', RuntimeWarning, stacklevel=2)
