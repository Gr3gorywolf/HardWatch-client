import json

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