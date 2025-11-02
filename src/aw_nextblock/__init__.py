__version__ = "0.1.0"
__app_name__ = "aw-nextblock"

from .cli import cli
from .main import main

__all__ = ["cli", "main"]
