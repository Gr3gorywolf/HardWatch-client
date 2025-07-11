from notifypy import Notify
from config import DISABLE_NOTIFICATIONS
def show_notification(title, message):
    if(DISABLE_NOTIFICATIONS):
        return
    notification = Notify(
        default_notification_application_name="HardWatch",
        default_notification_icon="icon.ico",
    )
    notification.title = title
    notification.message = message
    notification.send()