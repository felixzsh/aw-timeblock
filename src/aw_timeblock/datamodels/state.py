import os
import platform
import json
from pathlib import Path
from typing import Optional
from datetime import datetime
from .entities import SessionState, TimeBlock


def get_state_dir() -> Path:
    system = platform.system()
    
    if system == "Linux":
        base_dir = Path.home() / ".local" / "share" / "aw-timeblock"
    elif system == "Darwin":
        base_dir = Path.home() / "Library" / "Application Support" / "aw-timeblock"
    elif system == "Windows":
        base_dir = Path(os.environ["APPDATA"]) / "aw-timeblock"
    else:
        base_dir = Path.home() / ".aw-timeblock"
    
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir

def _serialize_datetime(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return None
    return dt.isoformat()

def _deserialize_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    if dt_str is None:
        return None
    return datetime.fromisoformat(dt_str)

def _serialize_session_state(state: SessionState) -> dict:
    return {
        "name": state.name,
        "current_block_idx": state.current_block_idx,
        "started_at": _serialize_datetime(state.started_at),
        "finished_at": _serialize_datetime(state.finished_at),
        "blocks": [
            {
                "name": block.name,
                "planned_duration": block.planned_duration,
                "started_at": _serialize_datetime(block.started_at) if block.started_at else None,
                "finished_at": _serialize_datetime(block.finished_at) if block.finished_at else None
            }
            for block in state.blocks
        ]
    }

def _deserialize_session_state(data: dict) -> SessionState:
    blocks = []
    for block_data in data["blocks"]:
        blocks.append(TimeBlock(
            name=block_data["name"],
            planned_duration=block_data["planned_duration"],
            started_at=_deserialize_datetime(block_data["started_at"]) if block_data["started_at"] else None,
            finished_at=_deserialize_datetime(block_data["finished_at"]) if block_data["finished_at"] else None
        ))
    
    return SessionState(
        name=data["name"],
        blocks=blocks,
        current_block_idx=int(data["current_block_idx"]),
        started_at=_deserialize_datetime(data["started_at"]),
        finished_at=_deserialize_datetime(data["finished_at"])
    )

def get_state_path() -> Path:
    return get_state_dir() / "session_state.json"

def session_exists() -> bool:
    return get_state_path().exists()

def load_session_state() -> Optional[SessionState]:
    state_path = get_state_path()
    
    if not state_path.exists():
        return None

    try:
        with open(state_path, 'r') as f:
            data = json.load(f)
        return _deserialize_session_state(data)
    except (json.JSONDecodeError, KeyError, TypeError):
        return None

def save_session_state(state: SessionState) -> bool:
    try:
        state_path = get_state_path()
        state_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(state_path, 'w') as f:
            json.dump(_serialize_session_state(state), f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

def delete_session_state() -> bool:
    try:
        state_path = get_state_path()
        if state_path.exists():
            state_path.unlink()
            return True
        return False
    except Exception:
        return False
