import logging
import time
from datetime import datetime
from typing import Optional

from aw_nextblock.reporter import ActivityWatchReporter
from .session import load_session


logger = logging.getLogger(__name__)


class SessionMonitor:
    def __init__(self):
        self.running = False
        self.cycle_count = 0
        self.start_time: Optional[datetime] = None
        self.aw_reporter: Optional[ActivityWatchReporter] = None
 
    def initialize(self) -> bool:
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
        try:
            session = load_session()

            if session:
                if self.aw_reporter:
                    self.aw_reporter.send_heartbeat(session)
            else:
                pass

        except Exception as e:
            logger.error(f"Error in monitoring cycle {self.cycle_count}: {e}")

        self.cycle_count += 1

    def run(self) -> None:
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
            if self.aw_reporter:
                self.aw_reporter.cleanup()

        logger.info("aw-watcher-nextblock monitoring stopped")

    def stop(self) -> None:
        self.running = False
