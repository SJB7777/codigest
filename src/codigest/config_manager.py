import json
from pathlib import Path
from typing import Optional
from platformdirs import user_config_dir

APP_NAME = "codigest"

class ConfigManager:
    def __init__(self):
        self.config_dir = Path(user_config_dir(APP_NAME))
        self.config_file = self.config_dir / "config.json"
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()

    def _load_config(self) -> dict:
        if not self.config_file.exists():
            return {}
        try:
            return json.loads(self.config_file.read_text(encoding='utf-8'))
        except Exception:
            return {}

    def save_config(self):
        try:
            self.config_file.write_text(json.dumps(self.config, indent=2), encoding='utf-8')
        except Exception as e:
            print(f"⚠️ Failed to save config: {e}")

    def get_last_project_root(self) -> Optional[str]:
        return self.config.get("last_project_root")

    def set_last_project_root(self, path: str):
        self.config["last_project_root"] = str(path)
        self.save_config()