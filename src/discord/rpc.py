import threading
import time
import pypresence
from monitor.collector import get_system_info
import config

CLIENT_ID = "1353474060364812308"
rpc = None
discord_thread = None

def update_presence(device_name="Unknown Device", device_type="desktop", cpu_name="Unknown CPU", gpu_name="Unknown GPU"):
    start_timestamp = int(time.time())
    while True:
        try:
            system_info = get_system_info(cpu_name, gpu_name, "errors-log.txt")
            rpc.update(
                state=f"📊 Usage: CPU {system_info['cpuUsage']}% | GPU {system_info['gpuUsage']}% | RAM {system_info['ramUsage']}% | Disk {system_info['diskUsage']}%"[:128], 
                details=f"👩🏾‍💻 Specs: Device {device_name[:15]} | CPU {cpu_name[-10:]} | GPU {gpu_name[-17:]} | RAM {system_info['ram'][-20:]} | Disk {system_info['disk'][-20:]}"[:128],
                large_image=device_type,
                large_text=f"Using {device_name}",
                small_text="System Monitor",
                start=start_timestamp,
            )
        except Exception as e:
            print(f"Failed to update Discord presence: {e}")

        time.sleep(5)

def init_discord_RPC():
    global discord_thread, rpc
    try:
        rpc = pypresence.Presence(CLIENT_ID)
    except Exception as e:
        print(f"Failed to initialize Discord RPC: {e}")
        return
    while True:
        try:
            print("Trying to connect to Discord RPC...")
            rpc.connect()
            print("Connected to Discord RPC successfully.")

            discord_thread = threading.Thread(target=update_presence, args=(config.DEVICE_NAME,config.DEVICE_TYPE , config.CPU_NAME, config.GPU_NAME), daemon=True)
            discord_thread.start()
            break
        except Exception as e:
            print(f"Could not connect to Discord RPC: {e}. Retrying in 30 seconds...")
            time.sleep(30)