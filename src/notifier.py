from notifypy import Notify
from typing import Optional

def notify_send(
    title: str,
    message: str,
    icon: Optional[str] = None,
    audio: Optional[str] = None,
    application_name: Optional[str] = None
) -> None:
    """
    Send a desktop notification non-blocking.
    Args:
        title: Notification title
        message: Notification message
        icon: Path to icon file (optional)
        audio: Path to audio file (optional)
        application_name: Application name (optional)
    """
    notification = Notify()
    notification.title = title
    notification.message = message
    if icon:
        notification.icon = icon
    if audio:
        notification.audio = audio
    if application_name:
        notification.application_name = application_name
    notification.send(block=False)
