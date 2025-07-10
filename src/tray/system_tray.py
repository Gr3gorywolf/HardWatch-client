
import webbrowser

from config import BACKEND_URL, DEVICE_ID
from tray.notifications import show_notification


SystemTray = None
def quit_app(icon, item):
    icon.stop()

def open_dashboard():
    webbrowser.open(BACKEND_URL + "/device/" + DEVICE_ID)

try:
    from pystray import Icon, MenuItem, Menu
    from PIL import Image
    icon_image = Image.open("icon.ico")
    menu = Menu(MenuItem("Open dashboard", open_dashboard),MenuItem("Quit", quit_app))
    SystemTray = Icon("HardWatch",icon=icon_image, menu=menu, title="HardWatch")
except:
    SystemTray = None
    pass

def init_tray():
    global SystemTray
    if SystemTray is None:
        print(f"No desktop environment detected.")
        return None
    try:
        SystemTray.run()
    except Exception as e:
        return None
    return SystemTray