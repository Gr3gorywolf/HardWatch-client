import hashlib
import json
from cpuinfo import get_cpu_info
from monitor.collector import get_device_uuid, get_gpu_name

CONFIG_FILE = "config.json"
ERROR_LOG = "errors-log.txt"
CONFIG = {}
APP_KEY = ""
DEVICE_NAME = ""
BACKEND_URL = ""
ACTIONABLES = []
SERVICES = []
DISABLE_NOTIFICATIONS = False
ENABLE_DISCORD_RPC = False
DEVICE_TYPE = "desktop"
USE_DOCKER_SERVICES = False
CPU_NAME = get_cpu_info().get("brand_raw", "Unknown CPU")
GPU_NAME = get_gpu_name()
DEVICE_ID = (
    get_device_uuid() or hashlib.sha1((DEVICE_NAME + CPU_NAME).encode()).hexdigest()
)


def load_config():
    global CONFIG, APP_KEY, DEVICE_NAME, BACKEND_URL, ACTIONABLES, SERVICES, DISABLE_NOTIFICATIONS, ENABLE_DISCORD_RPC, DEVICE_TYPE, USE_DOCKER_SERVICES
    try:
            file_content = open(CONFIG_FILE, "r")
            CONFIG = json.load(file_content)
    except FileNotFoundError:
        print(f"Configuration file '{CONFIG_FILE}' not found. Using default settings.")

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from '{CONFIG_FILE}': {e}")
        CONFIG = {}
    APP_KEY = CONFIG.get("appKey", "")
    DEVICE_NAME = CONFIG.get("name", "")
    BACKEND_URL = CONFIG.get("backendUrl", "")
    ACTIONABLES = CONFIG.get("actionables", [])
    SERVICES = CONFIG.get("services", [])
    DISABLE_NOTIFICATIONS = CONFIG.get("disableNotifications", False)
    ENABLE_DISCORD_RPC = CONFIG.get("enableDiscordRPC", False)
    DEVICE_TYPE = CONFIG.get("type", "desktop")
    USE_DOCKER_SERVICES = CONFIG.get("includeDockerServices", False)


load_config()
