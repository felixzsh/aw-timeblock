import json
import yaml
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from aw_core.dirs import get_cache_dir
import os
import tempfile
import logging

logger = logging.getLogger(__name__)

def get_session_path() -> Path:
    cache_dir = Path(get_cache_dir("aw-nextblock"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "session.json"

def session_exists() -> bool:
    return get_session_path().exists()

@dataclass
class TimeBlock:
    name: str
    planned_duration: int
    start_dt: Optional[datetime] = None

    @property
    def elapsed_time(self) -> float:
        if self.start_dt:
            return (datetime.now() - self.start_dt).total_seconds()
        return 0.0

@dataclass
class Session:
    name: str
    blocks: List[TimeBlock]
    current_block_idx: int
    start_dt: Optional[datetime] = None

    @property
    def current_block(self) -> Optional[TimeBlock]:
        if self.current_block_idx < len(self.blocks):
            return self.blocks[self.current_block_idx]
        return None

    @property
    def elapsed_time(self) -> float:
        if self.start_dt:
            return (datetime.now() - self.start_dt).total_seconds()
        return 0.0

    @classmethod
    def from_plan(cls, file_path_str: str) -> Optional['Session']:
        '''
        loads initial session state from yaml work session plan file
        '''
        try:
            file_path = Path(file_path_str)
            if not file_path.exists():
                return None
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            if not data or 'name' not in data:
                return None
            blocks = []
            for block_data in data.get('blocks', []):
                if 'name' not in block_data or 'duration' not in block_data:
                    continue
                blocks.append(TimeBlock(
                    name=str(block_data['name']),
                    planned_duration=int(block_data['duration']),
                ))
            return cls(
                name=str(data['name']),
                blocks=blocks,
                current_block_idx=0,
                start_dt=datetime.now()
            )
        except yaml.YAMLError:
            logger.error(f"Failed to parse YAML file: {file_path_str}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while loading session from plan: {e}")
            return None

def _serialize_datetime(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return None
    return dt.isoformat()

def _deserialize_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    if dt_str is None:
        return None
    return datetime.fromisoformat(dt_str)

def _serialize(session: Session) -> dict:
    return {
        "name": session.name,
        "current_block_idx": session.current_block_idx,
        "start_dt": _serialize_datetime(session.start_dt),
        "blocks": [
            {
                "name": block.name,
                "planned_duration": block.planned_duration,
                "start_dt": _serialize_datetime(block.start_dt)
            }
            for block in session.blocks
        ]
    }

def _deserialize(data: dict) -> Session:
    blocks = []
    for block_data in data["blocks"]:
        blocks.append(TimeBlock(
            name=block_data["name"],
            planned_duration=block_data["planned_duration"],
            start_dt=_deserialize_datetime(block_data['start_dt'])
        ))

    return Session(
        name=data["name"],
        blocks=blocks,
        current_block_idx=int(data["current_block_idx"]),
        start_dt=_deserialize_datetime(data["start_dt"]),
    )

#TODO raise respective errors instead of returning None
# and no not handle errors here, let the propagate
def load_session() -> Optional[Session]:
    session_path = get_session_path()
    if not session_path.exists():
        return None
    try:
        with open(session_path, 'r') as f:
            data = json.load(f)
        return _deserialize(data)
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.error(f"Failed to load session data: {e}")
        return None

def save_session(session: Session) -> bool:
    try:
        session_path = get_session_path()
        session_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode='w', 
            delete=False,
            dir=session_path.parent,
            suffix='.tmp'
        ) as tmp_file:
            json.dump(_serialize(session), tmp_file, indent=2, ensure_ascii=False)
            temp_path = tmp_file.name
        os.replace(temp_path, session_path)
        return True
    except Exception as e:
        logger.error(f"Failed to save session: {e}")
        return False

def delete_session() -> bool:
    try:
        session_path = get_session_path()
        if session_path.exists():
            session_path.unlink()
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to delete session: {e}")
        return False