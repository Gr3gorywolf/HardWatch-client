from notifypy import Notify
import config


def show_notification(title, message):
    if config.DISABLE_NOTIFICATIONS:
        return
    try:
        notification = Notify(
            default_notification_application_name="HardWatch",
            default_notification_icon="icon.ico",
        )
        notification.title = title
        notification.message = message
        notification.send()
    except Exception as e:
        print(f"Failed to send notification: {e}")
        return
