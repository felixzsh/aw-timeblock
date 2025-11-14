__version__ = "1.1.0"

try:
    from importlib.metadata import version
    __version__ = version("aw-nextblock")
except Exception:
    pass

__app_name__ = "aw-nextblock"
from .cli import cli
__all__ = ["cli"]
