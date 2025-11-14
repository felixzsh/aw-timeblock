import logging
import time
import asyncio
from datetime import datetime, timezone
from aw_core.models import Event
from aw_client import ActivityWatchClient
from aw_core.log import setup_logging
from aw_core.config import load_config_toml
from desktop_notifier import DesktopNotifier

from .session import load_session

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = """
[aw-watcher-nextblock]
poll_time = 1.0
notifications_enabled = true
notify_before_minutes = 5
notify_after_every_minutes = 5
time_scale_factor = 1
""".strip()

async def watcher_async(testing=False, verbose=False):

    aw = ActivityWatchClient("aw-watcher-nextblock", testing=testing)

    config = load_config_toml(aw.client_name, DEFAULT_CONFIG)
    poll_time = float(config[aw.client_name].get("poll_time"))
    notifications_enabled = config[aw.client_name].get("notifications_enabled")
    notify_before_minutes = int(config[aw.client_name].get("notify_before_minutes"))
    notify_after_every_minutes = int(config[aw.client_name].get("notify_after_every_minutes"))
    if testing:
        time_scale_factor = float(config[aw.client_name].get("time_scale_factor"))
    else:
        time_scale_factor = 1.0
    setup_logging(
        name=aw.client_name,
        testing=testing,
        verbose=verbose,
        log_stderr=True,
        log_file=True,
    )
 
    bucket_id = f"{aw.client_name}_{aw.client_hostname}"
    aw.create_bucket(bucket_id, event_type="timeblock", queued=True)
    aw.connect()
    logger.info("aw-watcher-nextblock started")
    session = None
    notifier = DesktopNotifier(
        app_name=aw.client_hostname,
        app_icon=None
    )
    last_notifications = {}

    async def handle_notifications(session, last_notifications, time_scale_factor):
        """Handle before, at, and after notifications for current block"""
        if not session or not session.current_block:
            return

        block = session.current_block
        if block.start_dt is None:
            return

        elapsed_seconds = block.elapsed_time * time_scale_factor
        planned_seconds = block.planned_duration * 60

        # BEFORE notification
        before_threshold_seconds = planned_seconds - notify_before_minutes * 60
        if elapsed_seconds >= before_threshold_seconds:
            if f"before_{block.name}" not in last_notifications:
                last_notifications[f"before_{block.name}"] = True
                await notifier.send(
                    title=f"{session.name}",
                    message=f"{block.name} ends in {notify_before_minutes} minutes",
                    icon=None
                )
                logger.info(f"Sent BEFORE notification for block: {block.name}")

        # AT/AFTER notification (AT is interval 0, AFTER repeats every X minutes)
        if elapsed_seconds >= planned_seconds:
            time_over_seconds = elapsed_seconds - planned_seconds
            after_interval_seconds = notify_after_every_minutes * 60
            intervals_passed = int(time_over_seconds / after_interval_seconds)

            after_key = f"after_{block.name}_{intervals_passed}"
            if after_key not in last_notifications:
                last_notifications[after_key] = True
                if intervals_passed == 0:
                    await notifier.send(
                        title=f"{session.name}",
                        message=f"{block.name} reached {block.planned_duration} minutes!",
                        icon=None
                    )
                    logger.info(f"Sent AT notification for block: {block.name}")
                else:
                    accumulated_minutes = int(time_over_seconds / 60)
                    await notifier.send(
                        title=f"{session.name}",
                        message=f"Overtime: +{accumulated_minutes}m for {block.name}",
                        icon=None
                    )
                    logger.info(f"Sent AFTER notification for block: {block.name} (overtime: {accumulated_minutes}m)")

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
            if notifications_enabled:
                await handle_notifications(session, last_notifications, time_scale_factor)
        else:
            pass

        elapsed = time.time() - cycle_start
        sleep_time = max(0, poll_time - elapsed)
        if sleep_time > 0:
            await asyncio.sleep(sleep_time)
