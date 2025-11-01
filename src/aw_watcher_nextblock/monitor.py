"""Main loop for aw-watcher-nextblock.

This module provides background monitoring of nextblock sessions,
only operating when sessions are in active state.
"""

import logging
import time
from datetime import datetime
from typing import Optional

from shared import load_session_state
from aw_watcher_nextblock.reporter import ActivityWatchReporter


logger = logging.getLogger(__name__)


class SessionMonitor:
    """Main monitor class for monitoring nextblock sessions."""
    
    def __init__(self):
        self.running = False
        self.cycle_count = 0
        self.start_time: Optional[datetime] = None
        self.aw_reporter: Optional[ActivityWatchReporter] = None
        
    def initialize(self) -> bool:
        """Initialize the monitor and ActivityWatch reporter."""
        try:
            self.aw_reporter = ActivityWatchReporter()
            if not self.aw_reporter.initialize():
                logger.warning("Failed to initialize ActivityWatch client")
                return False
            return True
        except Exception as e:
            logger.error(f"Failed to initialize SessionMonitor: {e}")
            return False
        
    def cycle(self) -> None:
        """Execute one monitoring cycle."""
        try:
            session_state = load_session_state()
            
            if session_state and session_state.is_active:
                if self.aw_reporter:
                    self.aw_reporter.send_heartbeat(session_state)
            else:
                # Session is inactive, no action needed
                pass
        
        except Exception as e:
            logger.error(f"Error in monitoring cycle {self.cycle_count}: {e}")
        
        self.cycle_count += 1
    
    def run(self) -> None:
        """Run the main monitoring loop."""
        if not self.initialize():
            logger.error("Failed to initialize SessionMonitor, exiting")
            return
            
        self.running = True
        self.start_time = datetime.now()
        self.cycle_count = 0
        
        logger.info("Starting aw-watcher-nextblock monitoring")
        
        try:
            while self.running:
                cycle_start = time.time()
                
                self.cycle()
                
                elapsed = time.time() - cycle_start
                sleep_time = max(0, 1.0 - elapsed)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
        finally:
            # Ensure cleanup happens even if there's an exception
            if self.aw_reporter:
                self.aw_reporter.cleanup()
        
        logger.info("aw-watcher-nextblock monitoring stopped")
    
    def stop(self) -> None:
        """Stop the monitoring loop gracefully."""
        self.running = False