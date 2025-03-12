import multiprocessing
import os
import json
import socketio
import time
import threading
import requests 
import platform
from cpuinfo import get_cpu_info

from utils import get_gpu_name, get_system_info, start_socket_client


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
# Get CPU and GPU info
cpu_info = get_cpu_info()
CPU_NAME = cpu_info.get("brand_raw", "Unknown CPU")
GPU_NAME = get_gpu_name()

def quit_app(icon, item):
    icon.stop()

try:
    from pystray import Icon, MenuItem, Menu
    from PIL import Image
    icon_image = Image.open("icon.ico")
    menu = Menu(MenuItem("Quit", quit_app))
    icon = Icon("System Monitor", icon_image, menu=menu)
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
                    **system_info,
                    "platform": platform.system(),
                    "actionables": ACTIONABLES
                }
                print("Sending data...", payload)
                headers = {"appKey": APP_KEY}
                response = requests.post(f"{BACKEND_URL}/send-stats-data", json=payload, headers=headers)
                if response.status_code != 200:
                    raise Exception(f"Failed to send data. Status code: {response.status_code}")
        except Exception as e:
            with open(ERROR_LOG, "a") as log:
                log.write(f"{time.ctime()} - {str(e)}\n")
        time.sleep(3)



# Tray icon setup

# Start socket client for actions
start_socket_client(APP_KEY, DEVICE_NAME, BACKEND_URL, ACTIONABLES)
# Run threads
thread = threading.Thread(target=send_stats, name="send_stats", daemon=True)
thread.start()

if(icon != None):
    icon.run()
else:
    while True:
        time.sleep(1)
