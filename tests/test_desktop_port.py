import json
import os
from pathlib import Path
import sys
import tempfile
import time
import tkinter as tk
import unittest
from unittest.mock import patch
from urllib.request import Request, urlopen

from app_launcher import Launcher
from cs2_ace import AceServer
from jarvis_ui import App


class DesktopPortTests(unittest.TestCase):
    def test_xdg_application_search_and_launch(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            apps = root / 'applications'
            apps.mkdir()
            entry = apps / 'sample.desktop'
            entry.write_text('[Desktop Entry]\nType=Application\nName=Sample App\nExec=sample %U\n', encoding='utf-8')
            with patch('app_launcher.DATA_HOME', root), patch.dict(os.environ, {'XDG_DATA_DIRS': temp}):
                launcher = Launcher()
                self.assertEqual(launcher.refresh(), 1)
                with patch('app_launcher.launch') as launch:
                    launcher.open('sample')
                    launch.assert_called_once_with(('gio', 'launch', str(entry)))

    @unittest.skipUnless(sys.platform == 'linux', 'requires Linux loopback')
    def test_cs2_listener_receives_gsi_event(self):
        received = []
        server = AceServer(received.append, port=0, secret='test-gsi')
        self.addCleanup(server.close)
        payload = {
            'auth': {'token': 'test-gsi'},
            'provider': {'appid': 730, 'steamid': '123'},
            'player': {'steamid': '123', 'activity': 'playing', 'state': {'round_kills': 5}},
            'map': {'name': 'de_dust2', 'phase': 'live', 'mode': 'competitive', 'round': 1},
            'round': {'phase': 'live'},
        }
        url = f'http://127.0.0.1:{server.server.server_port}/'
        with urlopen(Request(url, data=json.dumps(payload).encode()), timeout=3) as result:
            self.assertEqual(result.status, 200)
        self.assertEqual(len(received), 1)

    @unittest.skipUnless(sys.platform == 'linux' and os.environ.get('DISPLAY'), 'requires X11')
    def test_gui_notes_overlay_and_lineups(self):
        import activation
        import product
        with tempfile.TemporaryDirectory() as temp:
            data = Path(temp)
            with (
                patch.object(activation, 'STATE', data / 'activation.json'),
                patch.object(product, 'PREFS', data / 'settings.json'),
                patch('jarvis_ui.DATA', data / 'phrases.json'),
                patch('extra_commands.DATA_DIR', data),
                patch('game_journal.ROOT', data),
                patch('cs2_ace.TOKEN_PATH', data / 'cs2-token.txt'),
                patch('jarvis_ui.App.setup_tray'),
                patch.object(tk.Tk, 'mainloop'),
            ):
                activation.save({'license': next(iter(activation.KEYS))})
                product.save(voice_output=False, wake_enabled=False, seen_version=product.VERSION)
                app = App()
                try:
                    app.toggle_overlay()
                    app.open_lineups()
                    self.assertTrue(app.overlay.window.winfo_exists())
                    self.assertTrue(app.lineups.window.winfo_exists())
                    app.dispatch('запиши заметку Проверка Linux')
                    deadline = time.monotonic() + 5
                    notes = data / 'notes.json'
                    while not notes.exists() and time.monotonic() < deadline:
                        app.root.update()
                        time.sleep(.02)
                    self.assertEqual(json.loads(notes.read_text(encoding='utf-8'))[0]['text'], 'Проверка Linux')
                finally:
                    app.quit()
