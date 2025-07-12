import multiprocessing
import sys, os
import threading
import time
from cpuinfo import get_cpu_info
from monitor.collector import get_gpu_name
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from monitor.scheduler import start_schedulers, stop_schedulers
import config
from transport.websocket_client import start_socket_client, stop_socket_client
from discord.rpc import init_discord_RPC
from tray.system_tray import init_tray
from notifypy import Notify
def main():
    start_schedulers()
    start_socket_client()
    if(config.ENABLE_DISCORD_RPC):
        init_discord_RPC()
    if(init_tray() == None):
        while True:
            time.sleep(1)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    config.CPU_NAME = get_cpu_info().get("brand_raw", "Unknown CPU")
    config.GPU_NAME = get_gpu_name()
    print(config.CPU_NAME, config.GPU_NAME)
    main()