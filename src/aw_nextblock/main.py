import logging
import time
from datetime import datetime, timezone
from aw_core.models import Event
from aw_client import ActivityWatchClient

from .session import load_session

logger = logging.getLogger(__name__)

def main():
    client_name = "aw-watcher-nextblock"
    client = None
    bucket_id = None
    cycle_count = 0
    
    try:
        client = ActivityWatchClient(client_name, testing=True)
        bucket_id = f"{client_name}_{client.client_hostname}"
        client.create_bucket(bucket_id, event_type="nextblock-session")
        client.connect()
        logger.info("ActivityWatch client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize ActivityWatch client: {e}")
        return

    logger.info("Starting aw-watcher-nextblock monitoring")
    
    try:
        while True:
            cycle_start = time.time()
            
            try:

                #TODO better error handling for session loading
                session = load_session()
                
                if session and session.current_block:
                    heartbeat_data = {
                        "session": session.name,
                        "block": session.current_block.name,
                        "planned_duration": session.current_block.planned_duration,
                    }
                    now = datetime.now(timezone.utc)
                    heartbeat_event = Event(timestamp=now, data=heartbeat_data)
                    client.heartbeat(bucket_id, heartbeat_event, pulsetime=2.0, queued=True)
            except Exception as e:
                logger.error(f"Error in monitoring cycle {cycle_count}: {e}")
            
            cycle_count += 1
            
            elapsed = time.time() - cycle_start
            sleep_time = max(0, 1.0 - elapsed)
            
            if sleep_time > 0:
                time.sleep(sleep_time)
    finally:
        if client:
            client.disconnect()
            logger.info("ActivityWatch client disconnected")
    

if __name__ == "__main__":
    main()