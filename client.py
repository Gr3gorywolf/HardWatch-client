import multiprocessing
import os
import json
import subprocess
import socketio
import time
import threading
import requests
import psutil
import platform
from cpuinfo import get_cpu_info 
sio = socketio.Client()
try:
    from pynvml import nvmlInit, nvmlShutdown, nvmlDeviceGetHandleByIndex, nvmlDeviceGetUtilizationRates, nvmlDeviceGetTemperature, NVML_TEMPERATURE_GPU, nvmlDeviceGetName
    nvmlInit()
    NVIDIA_AVAILABLE = True
except :
    NVIDIA_AVAILABLE = False
    print("NVML no disponible en este entorno")

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



# Helper function to format storage
def format_storage(value_gb):
    """Format storage values, converting to TB if >= 1000GB"""
    if value_gb >= 1000:
        return f"{value_gb / 1000:.1f}TB"
    return f"{value_gb}GB"


# Get system info function
def get_system_info():
    try:
        # Get CPU info
        cpu_count = psutil.cpu_count(logical=False)
        cpu_threads = psutil.cpu_count(logical=True)
        cpu_usage = psutil.cpu_percent()

        # Get RAM info
        ram = psutil.virtual_memory()
        ram_total = ram.total // (1024**3)  # GB
        ram_used = ram.used // (1024**3)  # GB
        ram_usage = ram.percent

        # Get Disk info
        disks = psutil.disk_partitions()
        disk_total = sum(psutil.disk_usage(d.mountpoint).total for d in disks) // (1024**3)  # GB
        disk_used = sum(psutil.disk_usage(d.mountpoint).used for d in disks) // (1024**3)  # GB
        disk_usage = psutil.disk_usage('/').percent

        # Get GPU info
        gpu_usage = 0
        gpu_temp = None
        gpu_name = "Unknown GPU"
        gpu_model = "Unknown Model"

        if NVIDIA_AVAILABLE:
            try:
                handle = nvmlDeviceGetHandleByIndex(0)
                gpu_usage = nvmlDeviceGetUtilizationRates(handle).gpu
                gpu_temp = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
                gpu_name = nvmlDeviceGetName(handle)
                gpu_model = gpu_name.split(' ')[0]  # Extract the model name (e.g., GTX 1080)
            except Exception as e:
                with open(ERROR_LOG, "a") as log:
                    log.write(f"{time.ctime()} - Error getting NVIDIA GPU data: {str(e)}\n")
        else:
            # AMD & Intel fallback
            try:
                import pyadl  # AMD
                gpu_usage = pyadl.get_gpu_usage()
                gpu_name = "AMD GPU"
                gpu_model = "AMD GPU"
            except:
                try:
                    gpu_usage = 0
                    gpu_name = "Intel GPU"
                    gpu_model = "Intel GPU"
                except:
                    pass

        # Get CPU temperature
        cpu_temp = None
        try:
            temps = psutil.sensors_temperatures()
            if "coretemp" in temps:
                cpu_temp = sum(t.current for t in temps["coretemp"]) / len(temps["coretemp"])
        except:
            pass

        # Format values
        cpu_info = get_cpu_info()
        cpu_info = cpu_info.get("brand_raw", "Unknown CPU") + " " + f"{cpu_count}c/{cpu_threads}t"
        ram_info = f"{format_storage(ram_used)} / {format_storage(ram_total)}"
        disk_info = f"{format_storage(disk_used)} / {format_storage(disk_total)}"

        return {
            "cpuUsage": cpu_usage,
            "gpuUsage": gpu_usage,
            "gpuName": gpu_name,
            "gpuModel": gpu_model,
            "ramUsage": ram_usage,
            "diskTotal": disk_usage,
            "os": platform.platform(),
            "cpu": cpu_info,
            "gpu": gpu_name,
            "ram": ram_info,
            "disk": disk_info,
            "cpuTemp": cpu_temp,
            "gpuTemp": gpu_temp
        }
    except Exception as e:
        with open(ERROR_LOG, "a") as log:
            log.write(f"{time.ctime()} - Error in get_system_info: {str(e)}\n")
        return None

# Send data function
def send_stats():
    while True:
        try:
            system_info = get_system_info()
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


## Socket IO setup
@sio.event
def connect():
    print("Connected to server")

@sio.event
def disconnect():
    print("Disconnected from server")

@sio.on("execute-action")
def handle_action(data):
    action_name = data["action"]
    print(f"Executing action: {action_name}")

    # Buscar la acción en la lista de `actionables`
    action_command = None
    for item in ACTIONABLES:
        if item["name"].lower() == action_name.lower():
            action_command = item["action"]
            break

    if action_command:
        print(f"Running command: {action_command}")
        os.system(action_command)
    else:
        print(f"Action '{action_name}' not found in actionables")

try:
    sio.connect(BACKEND_URL, auth={"appKey": APP_KEY, "deviceName": DEVICE_NAME})
except:
    print("Error connecting to socket server")
    pass
# Tray icon setup
def quit_app(icon, item):
    icon.stop()
    if NVIDIA_AVAILABLE:
        nvmlShutdown()

# Run threads
thread = threading.Thread(target=send_stats, name="send_stats", daemon=True)
thread.start()
try:
    from pystray import Icon, MenuItem, Menu
    from PIL import Image
    icon_image = Image.open("icon.ico")
    menu = Menu(MenuItem("Quit", quit_app))
    icon = Icon("System Monitor", icon_image, menu=menu)
    icon.run()
except:
    while True:
        time.sleep(1)
    pass
