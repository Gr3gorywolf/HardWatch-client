
import multiprocessing
import sys, os
import hashlib
import time
import threading
import requests
import platform
from cpuinfo import get_cpu_info




sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from monitor.scheduler import start_schedulers
from monitor.collector import get_gpu_name, get_system_info, get_device_uuid
from config import USE_DOCKER_SERVICES, DEVICE_NAME, DEVICE_TYPE, APP_KEY, BACKEND_URL, ACTIONABLES, SERVICES, ENABLE_DISCORD_RPC, ERROR_LOG
from monitor.running_services import check_service_status, parse_services, get_docker_services
from transport.websocket_client import start_socket_client
from discord.rpc import init_presence
from tray.system_tray import init_tray
multiprocessing.freeze_support()

cpu_info = get_cpu_info()
CPU_NAME = cpu_info.get("brand_raw", "Unknown CPU")
GPU_NAME = get_gpu_name()
DEVICE_ID = get_device_uuid() or hashlib.sha1((DEVICE_NAME + CPU_NAME).encode()).hexdigest()


def main():
    start_socket_client(APP_KEY, DEVICE_ID, BACKEND_URL, ACTIONABLES)
    start_schedulers()
    if(ENABLE_DISCORD_RPC):
        init_presence(DEVICE_NAME,DEVICE_TYPE, CPU_NAME, GPU_NAME)

    if(init_tray() == None):
        while True:
            time.sleep(1)

if __name__ == "__main__":
    main()