"""Main loop for aw-nextblock session management."""
import logging
import time
from datetime import datetime
from typing import Optional

from .core import initialize_session_watcher, send_heartbeat
from .core.entities import SessionPlan


logger = logging.getLogger(__name__)


class MainLoop:
    
    def __init__(self, session_plan: Optional[SessionPlan] = None):
        self.running = False
        self.cycle_count = 0
        self.start_time: Optional[datetime] = None
        self.session_watcher_initialized = False
        self.session_plan = session_plan
        
    def cycle(self) -> None:
        if not self.session_watcher_initialized:
            initialize_session_watcher()
            self.session_watcher_initialized = True
        
        send_heartbeat()
        
    
    def run(self) -> None:
        self.running = True
        self.start_time = datetime.now()
        self.cycle_count = 0
        
        while self.running:
            cycle_start = time.time()
            
            try:
                self.cycle()
            except Exception as e:
                print(f"Error in cycle {self.cycle_count}: {e}")
            
            self.cycle_count += 1
            
            # Calculate precise timing for next cycle
            elapsed = time.time() - cycle_start
            sleep_time = max(0, 1.0 - elapsed)
            
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def stop(self) -> None:
        """Stop the main loop gracefully."""
        self.running = False