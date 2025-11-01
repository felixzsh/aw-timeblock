import os
import platform
import json
from pathlib import Path
from typing import Optional
from datetime import datetime
from .entities import SessionState, TimeBlock, SessionStatus


def get_state_dir() -> Path:
    system = platform.system()
    
    if system == "Linux":
        base_dir = Path.home() / ".local" / "share" / "aw-nextblock"
    elif system == "Darwin":
        base_dir = Path.home() / "Library" / "Application Support" / "aw-nextblock"
    elif system == "Windows":
        base_dir = Path(os.environ["APPDATA"]) / "aw-nextblock"
    else:
        base_dir = Path.home() / ".aw-nextblock"
    
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

def _serialize_session_status(status: SessionStatus) -> str:
    return status.value

def _deserialize_session_status(status_str: str) -> SessionStatus:
    return SessionStatus(status_str)

def _serialize_session_state(state: SessionState) -> dict:
    return {
        "name": state.name,
        "current_block_idx": state.current_block_idx,
        "status": _serialize_session_status(state.status),
        "start_dt": _serialize_datetime(state.start_dt),
        "end_dt": _serialize_datetime(state.end_dt),
        "blocks": [
            {
                "name": block.name,
                "planned_duration": block.planned_duration,
                "start_dt": _serialize_datetime(block.start_dt) if block.start_dt else None,
                "end_dt": _serialize_datetime(block.end_dt) if block.end_dt else None
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
            start_dt=_deserialize_datetime(block_data["start_dt"]) if block_data["start_dt"] else None,
            end_dt=_deserialize_datetime(block_data["end_dt"]) if block_data["end_dt"] else None
        ))
    
    # Handle backward compatibility - if status field is missing, default to INACTIVE
    status_str = data.get("status", "inactive")
    status = _deserialize_session_status(status_str)
    
    return SessionState(
        name=data["name"],
        blocks=blocks,
        current_block_idx=int(data["current_block_idx"]),
        status=status,
        start_dt=_deserialize_datetime(data["start_dt"]),
        end_dt=_deserialize_datetime(data["end_dt"])
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

def create_session_state(name: str, blocks: list[TimeBlock]) -> SessionState:
    """Create a new session state from a plan."""
    return SessionState(
        name=name,
        blocks=blocks,
        current_block_idx=0,
        status=SessionStatus.ACTIVE,
        start_dt=datetime.now()
    )


def advance_session_state(session_state: SessionState) -> SessionState:
    """Advance the session state to the next block."""
    # Mark current block as completed
    if session_state.current_block:
        session_state.blocks[session_state.current_block_idx].end_dt = datetime.now()
    
    # Move to next block
    next_block_idx = session_state.current_block_idx + 1
    
    if next_block_idx < len(session_state.blocks):
        # Start next block
        session_state.current_block_idx = next_block_idx
        session_state.blocks[next_block_idx].start_dt = datetime.now()
    else:
        # No more blocks, end session
        session_state.status = SessionStatus.INACTIVE
        session_state.end_dt = datetime.now()
    
    return session_state


def delete_session_state() -> bool:
    try:
        state_path = get_state_path()
        if state_path.exists():
            state_path.unlink()
            return True
        return False
    except Exception:
        return False