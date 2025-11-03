import logging
import time
import argparse
from datetime import datetime, timezone
from aw_core.models import Event
from aw_client import ActivityWatchClient
from aw_core.log import setup_logging
from aw_core.config import load_config_toml

from .session import load_session

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = """
[aw-watcher-nextblock]
poll_time = 1.0
notifications_enabled = true
notify_before_minutes = 5
notify_after_every_minutes = 10
""".strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--testing", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    aw = ActivityWatchClient("aw-watcher-nextblock", testing=args.testing)

    config = load_config_toml(aw.client_name, DEFAULT_CONFIG)
    poll_time = float(config[aw.client_name].get("poll_time"))
    notifications_enabled = config[aw.client_name].get("notifications_enabled")
    notify_before_minutes = int(config[aw.client_name].get("notify_before_minutes"))
    notify_after_every_minutes = int(config[aw.client_name].get("notify_after_every_minutes"))

    setup_logging(
        name=aw.client_name,
        testing=args.testing,
        verbose=args.verbose,
        log_stderr=True,
        log_file=True,
    )
    
    bucket_id = f"{aw.client_name}_{aw.client_hostname}"
    aw.create_bucket(bucket_id, event_type="timeblock", queued=True)
    aw.connect()

    logger.info("aw-watcher-nextblock started")

    cycle_count = 0
    session = None
    while True:
        cycle_start = time.time()
        try:
            #TODO: add better error handling for session loading 
            session = load_session()
        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")

        if session and session.current_block:
            heartbeat_data = {
                "session": session.name,
                "block": session.current_block.name,
                "planned_duration": session.current_block.planned_duration,
            }
            now = datetime.now(timezone.utc)
            heartbeat_event = Event(timestamp=now, data=heartbeat_data)
            aw.heartbeat(bucket_id, heartbeat_event, pulsetime=poll_time + 1.0, queued=True)
        else:
            pass
        cycle_count += 1
        elapsed = time.time() - cycle_start
        sleep_time = max(0, poll_time - elapsed)
        if sleep_time > 0:
            time.sleep(sleep_time)

if __name__ == "__main__":
    main()