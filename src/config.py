import hashlib
import json
from cpuinfo import get_cpu_info
from monitor.collector import get_device_uuid, get_gpu_name

CONFIG_FILE = "config.json"
ERROR_LOG = "errors-log.txt"
with open(CONFIG_FILE, "r") as f:
    config = json.load(f)
APP_KEY =  config.get("appKey", "")
DEVICE_NAME =  config.get("name", "")
BACKEND_URL =  config.get("backendUrl", "")
ACTIONABLES = config.get("actionables", [])
SERVICES = config.get("services", [])
ENABLE_DISCORD_RPC = config.get("enableDiscordRPC", False)
DEVICE_TYPE = config.get("type", "desktop")
USE_DOCKER_SERVICES = config.get("includeDockerServices", False)
CPU_NAME = get_cpu_info().get("brand_raw", "Unknown CPU")
GPU_NAME = get_gpu_name()
DEVICE_ID = get_device_uuid() or hashlib.sha1((DEVICE_NAME + CPU_NAME).encode()).hexdigest()