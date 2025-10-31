from dataclasses import dataclass
import traceback
from typing import Optional
import tomllib
import traceback
import os
import platform
from pathlib import Path

def get_config_dir() -> Path:
    system = platform.system()

    if system == "Linux":
        base_dir = Path.home() / ".config" / "aw-timeblock"
    elif system == "Darwin":
        base_dir = Path.home() / "Library" / "Preferences" / "aw-timeblock"
    elif system == "Windows":
        base_dir = Path(os.environ["APPDATA"]) / "aw-timeblock"
    else:
        base_dir = Path.home() / ".aw-timeblock"

    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir

@dataclass
class NotificationConfig:
    enabled: bool = True
    sound: bool = True

@dataclass
class ServerConfig:
    host: str = "localhost"
    port: int = 5600

    @property
    def server_url(self) -> str:
        return f"http://{self.host}:{self.port}"

@dataclass
class AppConfig:
    server: ServerConfig
    notifications: NotificationConfig

    def __post_init__(self):
        self.server = self.server or ServerConfig()
        self.notifications = self.notifications or NotificationConfig()

def _load_config() -> Optional[AppConfig]:
    config_file = get_config_dir() / "config.toml"


    if not config_file.exists():
        return None

    try:
        with open(config_file, 'rb') as f:
            data = tomllib.load(f)

        return AppConfig(
            server=ServerConfig(**data.get('server', {})),
            notifications=NotificationConfig(**data.get('notifications', {}))
        )
    except Exception:
        traceback.print_exc()
        return None

config: Optional[AppConfig] = _load_config()
