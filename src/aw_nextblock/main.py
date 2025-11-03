import logging
import time
from datetime import datetime, timezone
from aw_core.models import Event
from aw_client import ActivityWatchClient

from .session import load_session

logger = logging.getLogger(__name__)

def main():
    client = ActivityWatchClient("aw-watcher-nextblock", testing=True)
    bucket_id = f"{client.client_name}_{client.client_hostname}"
    client.create_bucket(bucket_id, event_type="timeblock")
    client.connect()

    logger.info("aw-watcher-nextblock started")
 
    cycle_count = 0
    session = None
    while True:
        cycle_start = time.time()

        try:
            #TODO better error handling for session loading
            session = load_session()
        except Exception as e:
            logger.exception(e)

        if session and session.current_block:
            heartbeat_data = {
                "session": session.name,
                "block": session.current_block.name,
                "planned_duration": session.current_block.planned_duration,
            }
            now = datetime.now(timezone.utc)
            heartbeat_event = Event(timestamp=now, data=heartbeat_data)
            client.heartbeat(bucket_id, heartbeat_event, pulsetime=2.0, queued=True)
        else:
            pass

        cycle_count += 1

        elapsed = time.time() - cycle_start
        sleep_time = max(0, 1.0 - elapsed)

        if sleep_time > 0:
            time.sleep(sleep_time)


if __name__ == "__main__":
    main()
