import multiprocessing
import os
import hashlib
import json
import webbrowser
import psutil
import socketio
import time
import threading
import requests 
import platform
from cpuinfo import get_cpu_info

from utils import get_device_uuid, get_gpu_name, get_system_info, start_socket_client
from utils.discord_presence import init_presence


multiprocessing.freeze_support()
CONFIG_FILE = "config.json"
ERROR_LOG = "errors-log.txt"

# Load configuration
with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

APP_KEY = config["appKey"]
DEVICE_NAME = config["name"]
BACKEND_URL = config["backendUrl"]
ACTIONABLES = config["actionables"]
DEVICE_TYPE = config.get("type", "desktop")
# Get CPU and GPU info
cpu_info = get_cpu_info()
CPU_NAME = cpu_info.get("brand_raw", "Unknown CPU")
GPU_NAME = get_gpu_name()
DEVICE_ID = get_device_uuid() or hashlib.sha1((DEVICE_NAME + CPU_NAME).encode()).hexdigest()

def quit_app(icon, item):
    icon.stop()

def open_dashboard():
    webbrowser.open(BACKEND_URL + "/device/" + DEVICE_ID)

try:
    from pystray import Icon, MenuItem, Menu
    from PIL import Image
    icon_image = Image.open("icon.ico")
    menu = Menu(MenuItem("Open dashboard", open_dashboard),MenuItem("Quit", quit_app))
    icon = Icon("PCSpecTrack", icon_image, menu=menu)
except:
    icon = None 
    pass


# Send data function
def send_stats():
    while True:
        try:
            system_info = get_system_info(CPU_NAME, GPU_NAME, ERROR_LOG)
            if system_info:
                payload = {
                    "name": DEVICE_NAME,
                    "id": DEVICE_ID,
                    "type": DEVICE_TYPE,
                    **system_info,
                    "platform": platform.system(),
                    "actionables": ACTIONABLES
                }
                print("Sending data...", payload)
                headers = {"appKey": APP_KEY}
                response = requests.post(f"{BACKEND_URL}/api/devices/send-stats-data", json=payload, headers=headers)
                if response.status_code != 200:
                    raise Exception(f"Failed to send data. Status code: {response.status_code}")
        except Exception as e:
            with open(ERROR_LOG, "a") as log:
                log.write(f"{time.ctime()} - {str(e)}\n")
        time.sleep(3)



# Tray icon setup

# Start socket client for actions
start_socket_client(APP_KEY, DEVICE_ID, BACKEND_URL, ACTIONABLES)
# Run threads
thread = threading.Thread(target=send_stats, name="send_stats", daemon=True)
thread.start()

init_presence(DEVICE_NAME,DEVICE_TYPE, CPU_NAME, GPU_NAME)

if(icon != None):
    icon.run()
else:
    while True:
        time.sleep(1)
