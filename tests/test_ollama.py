import io
import json
import unittest
from unittest.mock import patch

from cli import ask_ollama


class OllamaTests(unittest.TestCase):
    @patch('cli.request.build_opener')
    def test_chat_sends_prompt_to_local_ollama(self, build_opener):
        opener = build_opener.return_value
        opener.open.return_value = io.BytesIO(b'{"response": " Linux "}')
        self.assertEqual(ask_ollama('Что такое Linux?', 'qwen3:4b'), 'Linux')
        query = opener.open.call_args.args[0]
        self.assertEqual(query.full_url, 'http://127.0.0.1:11434/api/generate')
        self.assertEqual(json.loads(query.data), {
            'model': 'qwen3:4b', 'prompt': 'Что такое Linux?', 'stream': False,
        })
