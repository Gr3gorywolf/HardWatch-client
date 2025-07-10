from notifypy import Notify
def show_notification(title, message):
    notification = Notify(
        default_notification_application_name="HardWatch",
        default_notification_icon="icon.ico",
    )
    notification.title = title
    notification.message = message
    notification.send()