"""
Session watcher for ActivityWatch integration.

Handles bucket initialization and sending heartbeat events based on
the current session state. This module will be called from the main loop.
"""

import sys
from datetime import datetime, timezone
from typing import Optional

from aw_core.models import Event
from aw_client import ActivityWatchClient

from .state import load_session_state
from ..config import config


class SessionWatcher:
    """ActivityWatch session watcher for aw-nextblock."""
    
    def __init__(self, client_name: str = "aw-nextblock"):
        """
        Initialize the session watcher.
        
        Args:
            client_name: Name for the ActivityWatch client
        """
        self.client_name = client_name
        self.client: Optional[ActivityWatchClient] = None
        self.bucket_id: Optional[str] = None
        
    def initialize(self) -> bool:
        """
        Initialize the ActivityWatch bucket.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.client = ActivityWatchClient(self.client_name, testing=True)
            
            self.bucket_id = f"{self.client_name}_{self.client.client_hostname}"
            
            self.client.create_bucket(self.bucket_id, event_type="nextblock-session")
            
            return True
            
        except Exception as e:
            print(f"Failed to initialize ActivityWatch client: {e}")
            return False
    
    def send_heartbeat(self) -> bool:
        """
        Send heartbeat based on current session state.
        
        This function should be called from the main loop cycle.
        It loads the current state and sends appropriate heartbeat events.
        
        Returns:
            True if heartbeat sent successfully, False otherwise
        """
        if not self.client or not self.bucket_id:
            return False
            
        try:
            session_state = load_session_state()
            
            if session_state is None:
                heartbeat_data = {
                    "session_status": "no_active_session"
                }
            else:
                current_block = None
                if session_state.current_block_idx < len(session_state.blocks):
                    current_block = session_state.blocks[session_state.current_block_idx]
                
                heartbeat_data = {
                    "session_name": session_state.name,
                    "session_status": "active",
                    "current_block_idx": session_state.current_block_idx,
                    "total_blocks": len(session_state.blocks),
                    "start_time": session_state.start_dt.isoformat() if session_state.start_dt else None,
                    "end_time": session_state.end_dt.isoformat() if session_state.end_dt else None
                }
                
                if current_block:
                    heartbeat_data.update({
                        "current_block_name": current_block.name,
                        "planned_duration": current_block.planned_duration,
                        "block_start_time": current_block.start_dt.isoformat() if current_block.start_dt else None,
                        "block_end_time": current_block.end_dt.isoformat() if current_block.end_dt else None
                    })
            
            now = datetime.now(timezone.utc)
            heartbeat_event = Event(timestamp=now, data=heartbeat_data)
            
            self.client.heartbeat(self.bucket_id, heartbeat_event, pulsetime=2.0, queued=True)
            
            return True
            
        except Exception as e:
            print(f"Failed to send heartbeat: {e}")
            return False
    
    def cleanup(self) -> None:
        """Cleanup resources."""
        if self.client:
            try:
                self.client.disconnect()
            except Exception:
                pass


_session_watcher: Optional[SessionWatcher] = None


def get_session_watcher() -> Optional[SessionWatcher]:
    """Get the global session watcher instance."""
    return _session_watcher


def initialize_session_watcher() -> bool:
    """
    Initialize the global session watcher.
    
    Returns:
        True if initialization successful, False otherwise
    """
    global _session_watcher
    
    _session_watcher = SessionWatcher()
    return _session_watcher.initialize()


def send_heartbeat() -> bool:
    """
    Send heartbeat using the global session watcher.
    
    This is the function that should be called from the main loop cycle.
    
    Returns:
        True if heartbeat sent successfully, False otherwise
    """
    global _session_watcher
    
    if _session_watcher is None:
        return False
        
    return _session_watcher.send_heartbeat()