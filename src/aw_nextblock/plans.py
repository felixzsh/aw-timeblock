"""Session plan loading and validation functionality."""
import logging
from pathlib import Path
from typing import Optional

import yaml

from shared import (
    SessionPlan, TimeBlock
)

logger = logging.getLogger(__name__)


def load_session_plan(file_path_str: str) -> Optional[SessionPlan]:
    """
    Load a YAML session plan file and deserialize it into a SessionPlan object.

    Args:
        file_path_str: Path to the YAML session plan file

    Returns:
        SessionPlan object if successful, None if there's an error
    """
    try:
        file_path = Path(file_path_str)
        
        if not file_path.exists():
            logger.error("Session plan file %s does not exist", file_path)
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if not data or 'name' not in data:
            logger.error("Invalid YAML structure: missing 'name' field for session plan")
            return None

        blocks = []
        for i, block_data in enumerate(data.get('blocks', [])):
            try:
                if 'name' not in block_data or 'duration' not in block_data:
                    logger.warning("Time block %d is incomplete: missing 'name' or 'duration'", i)
                    continue

                blocks.append(TimeBlock(
                    name=str(block_data['name']),
                    planned_duration=int(block_data['duration'])
                ))
            except (ValueError, TypeError) as e:
                logger.error("Error in time block %d: %s", i, e)
                continue

        return SessionPlan(
            name=str(data['name']),
            blocks=blocks
        )

    except yaml.YAMLError as e:
        logger.error("YAML syntax error in session plan: %s", e)
    except Exception as e:
        logger.error("Unexpected error loading session plan: %s", e)

    return None
