
import json
import os

from .config import CONFIG_DIR


class _Settings(dict):

    _FILE = os.path.join(CONFIG_DIR, 'settings.json')

    def save(self):
        try:
            with open(self._FILE, 'w', encoding='utf-8') as f:
                json.dump(
                    self, f, ensure_ascii=False, indent=2, sort_keys=True)
        except OSError:
            pass

    def load(self):
        try:
            with open(self._FILE, 'r', encoding='utf-8') as f:
                self.update(json.load(f))
        except (OSError, ValueError):
            pass


settings = _Settings()
