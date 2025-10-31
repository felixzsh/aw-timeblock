from typing import Optional
import yaml
from pathlib import Path
from .entities import SessionPlan, TimeBlock


def load_session_plan(file_path_str: str) -> Optional[SessionPlan]:
    """
    Load a YAML session plan file and deserialize it into a SessionPlan object.

    Args:
        file_path: Path to the YAML session plan file

    Returns:
        SessionPlan object if successful, None if there's an error
    """
    try:

        file_path = Path(file_path_str)
        # Check if file exists
        if not file_path.exists():
            print(f"Session plan file {file_path} does not exist")
            return None

        # Load and parse YAML
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # Validate basic structure
        if not data or 'name' not in data:
            print("Invalid YAML structure: missing 'name' field for session plan")
            return None

        # Process time blocks with validation
        blocks = []
        for i, block_data in enumerate(data.get('blocks', [])):
            try:
                if 'name' not in block_data or 'duration' not in block_data:
                    print(f"Time block {i} is incomplete: missing 'name' or 'duration'")
                    continue

                blocks.append(TimeBlock(
                    name=str(block_data['name']),
                    planned_duration=int(block_data['duration'])
                ))
            except (ValueError, TypeError) as e:
                print(f"Error in time block {i}: {e}")
                continue

        return SessionPlan(
            name=str(data['name']),
            blocks=blocks
        )

    except yaml.YAMLError as e:
        print(f"YAML syntax error in session plan: {e}")
    except Exception as e:
        print(f"Unexpected error loading session plan: {e}")

    return None
