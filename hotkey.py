from linux_desktop import WAYLAND

def parse(value):
    parts = [p.strip().upper() for p in value.split('+')]
    modifiers = {'CTRL': 2, 'ALT': 1, 'SHIFT': 4, 'WIN': 8}
    if len(parts) < 2 or len(set(parts)) != len(parts):
        raise ValueError('Пример: Ctrl+J или Ctrl+Shift+J')
    mask = 0
    for part in parts[:-1]:
        if part not in modifiers:
            raise ValueError('Используй Ctrl, Alt, Shift или Win.')
        mask |= modifiers[part]
    key = parts[-1]
    if len(key) == 1 and key in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789':
        vk = ord(key)
    elif key.startswith('F') and key[1:].isdigit() and 1 <= int(key[1:]) <= 24:
        vk = 111 + int(key[1:])
    else:
        raise ValueError('Последняя клавиша: латинская буква, цифра или F1–F24.')
    return mask, vk


class Hotkey:
    def __init__(self, root, callback):
        self.root = root
        self.callback = callback
        self.listener = None
        self.binding = None

    def set(self, value):
        mask, key = parse(value)
        modifiers = [pair for bit, pair in (
            (2, ('ctrl', 'Control')), (1, ('alt', 'Alt')),
            (4, ('shift', 'Shift')), (8, ('cmd', 'Super')),
        ) if mask & bit]
        letter = chr(key).lower() if key < 112 else f'f{key - 111}'
        if not WAYLAND:
            try:
                from pynput import keyboard
            except ImportError:
                keyboard = None
            if keyboard is not None:
                combo = '+'.join([f'<{pynput}>' for pynput, _ in modifiers]
                                 + [f'<{letter}>' if key >= 112 else letter])
                listener = keyboard.GlobalHotKeys({combo: self.callback})
                listener.start()
                self.close()
                self.listener = listener
                return
        tk_key = letter.upper() if key >= 112 or mask & 4 else letter
        sequence = '<' + '-'.join([tk for _, tk in modifiers] + ['KeyPress', tk_key]) + '>'
        self.close()
        binding = self.root.bind(sequence, lambda event: self.callback(), add='+')
        self.binding = (sequence, binding)

    def close(self):
        if self.listener is not None:
            self.listener.stop()
            self.listener = None
        if self.binding is not None:
            self.root.unbind(*self.binding)
            self.binding = None

