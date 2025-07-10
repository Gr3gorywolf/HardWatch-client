import multiprocessing
import os
import hashlib
import json
import webbrowser
import time
import threading
import requests 
import platform
from cpuinfo import get_cpu_info

from utils import get_device_uuid, get_gpu_name, get_system_info, start_socket_client, get_docker_services
from utils.discord_presence import init_presence
from utils.running_services import check_service_status, parse_services


multiprocessing.freeze_support()
CONFIG_FILE = "config.json"
ERROR_LOG = "errors-log.txt"

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

APP_KEY =  config.get("appKey", "")
DEVICE_NAME =  config.get("name", "")
BACKEND_URL =  config.get("backendUrl", "")
ACTIONABLES = config.get("actionables", [])
SERVICES = config.get("services", [])
ENABLE_DISCORD_RPC = config.get("enable-discord-rpc", False)
DEVICE_TYPE = config.get("type", "desktop")
USE_DOCKER_SERVICES = config.get("use-docker-services", False)
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
    icon = Icon("HardWatch",icon=icon_image, menu=menu, title="HardWatch")
except:
    icon = None 
    pass


def send_device_info():
    system_info = get_system_info(CPU_NAME, GPU_NAME, ERROR_LOG)
    parsed_services = parse_services(SERVICES)
    docker_services = get_docker_services()
    all_services = docker_services + parsed_services if USE_DOCKER_SERVICES else parsed_services
    if system_info:
        payload = {
            "name": DEVICE_NAME,
            "id": DEVICE_ID,
            "type": DEVICE_TYPE,
            **system_info,
            "platform": platform.system(),
            "actionables": ACTIONABLES,
            "services": all_services,
        }
        print("Sending data...")
        headers = {"appKey": APP_KEY}
        response = requests.post(f"{BACKEND_URL}/api/devices/send-stats-data", json=payload, headers=headers)
        return {
            "response": response,
            "payload": payload
        }

def send_stats():
    usage_thread_started = False
    while True:
        try:
            request = send_device_info()
            response = request.get("response")
            payload = request.get("payload")
            if response:
                if response.status_code != 200:
                    raise Exception(f"Failed to send data. Status code: {request.response.status_code}")
                else:
                    if usage_thread_started == False:
                        usage_thread_started = True
                        print("Starting usage thread...")
                        usage_thread = threading.Thread(target=send_usages, name="send_usages", daemon=True)
                        usage_thread.start()
                    results = []
                    for service in payload.get("services", []):
                        status = check_service_status(service)
                        results.append(status)
                    headers = {"appKey": APP_KEY}
                    print("Sending services data...")
                    requests.post(f"{BACKEND_URL}/api/devices/send-stats-data", json={
                        **payload,
                        "services": results
                    }, headers=headers)
                    time.sleep(60)
        except Exception as e:
            print(f"Error: {str(e)}")
            with open(ERROR_LOG, "a") as log:
                log.write(f"{time.ctime()} - {str(e)}\n")
        time.sleep(3)

def send_usages():
    while True:
        try:
            system_info = get_system_info(CPU_NAME, GPU_NAME, ERROR_LOG)
            if system_info:
                payload = {
                    "id": DEVICE_ID,
                    "battery": system_info.get("battery", None),
                    "cpuUsage": system_info.get("cpuUsage", 0),
                    "diskUsage": system_info.get("diskUsage", 0),
                    "ramUsage" : system_info.get("ramUsage", 0),
                    "gpuUsage": system_info.get("gpuUsage", 0),
                    "isCharging": system_info.get("isCharging", None),
                    "ram": system_info.get("ram", 0),
                    "disk": system_info.get("disk", 0),
                    "cpuTemp": system_info.get("cpuTemp", 0),
                    "gpuTemp": system_info.get("gpuTemp", 0),
                }
                print("Sending usage data...")
                headers = {"appKey": APP_KEY}
                response = requests.post(f"{BACKEND_URL}/api/devices/send-device-usage", json=payload, headers=headers)
                if response.status_code != 200:
                    if(response.status_code == 404):
                        print("Sending device info again...")
                        send_device_info()
                    else:
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
if(ENABLE_DISCORD_RPC):
    init_presence(DEVICE_NAME,DEVICE_TYPE, CPU_NAME, GPU_NAME)

if(icon != None):
    icon.run()
else:
    while True:
        time.sleep(1)
