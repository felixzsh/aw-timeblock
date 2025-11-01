"""
Main entry point for aw-watcher-nextblock.

This module is designed to be executed directly as a script,
following ActivityWatch watcher conventions.
"""

import signal
import sys
import logging

from aw_watcher_nextblock.monitor import SessionMonitor

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the watcher."""
    logger.info("Starting aw-watcher-nextblock")
    
    watcher = SessionMonitor()
    
    def signal_handler(signum, frame):
        watcher.stop()
        sys.exit(0)
    
    # Handle graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        watcher.run()
    except KeyboardInterrupt:
        watcher.stop()
    except Exception as e:
        logger.error(f"Fatal error in watcher: {e}")
        watcher.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()