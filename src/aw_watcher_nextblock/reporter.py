import logging
from datetime import datetime, timezone
from typing import Optional
from aw_core.models import Event
from aw_client import ActivityWatchClient

from shared.entities import SessionState

logger = logging.getLogger(__name__)

class ActivityWatchReporter:
    def __init__(self, client_name: str = "aw-watcher-nextblock"):
        self.client_name = client_name
        self.client: Optional[ActivityWatchClient] = None
        self.bucket_id: Optional[str] = None
        self._initialized = False

    def initialize(self) -> bool:
        try:
            if self._initialized:
                return True
            self.client = ActivityWatchClient(self.client_name, testing=True)
            self.bucket_id = f"{self.client_name}_{self.client.client_hostname}"
            self.client.create_bucket(self.bucket_id, event_type="nextblock-session")
            self.client.connect()
            self._initialized = True
            return True
 
        except Exception as e:
            logger.error(f"Failed to initialize aw client: {e}")
            return False
    
    def send_heartbeat(self, session_state: SessionState) -> bool:
        if not self.client or not self.bucket_id:
            logger.warning("aw not intialized")
            return False
        try:
            current_block = session_state.current_block
            if session_state.is_active and current_block:
                heartbeat_data = {
                    "session": session_state.name,
                    "block": current_block.name,
                    "planned_duration": current_block.planned_duration,
                }
                now = datetime.now(timezone.utc)
                heartbeat_event = Event(timestamp=now, data=heartbeat_data)
                self.client.heartbeat(self.bucket_id, heartbeat_event, pulsetime=2.0, queued=True)
            else:
                return False
            return True
        except Exception as e:
            print(f"Failed to send heartbeat: {e}")
            return False
    def cleanup(self) -> None:
        if self.client:
            self.client.disconnect()
