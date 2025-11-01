import signal
import sys
import logging

from .monitor import SessionMonitor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    logger.info("Starting aw-watcher-nextblock")

    watcher = SessionMonitor()

    def signal_handler(signum, frame):
        watcher.stop()
        sys.exit(0)

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