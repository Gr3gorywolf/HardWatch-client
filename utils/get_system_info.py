import platform
import time
import psutil
try:
    from pynvml import nvmlInit, nvmlShutdown, nvmlDeviceGetHandleByIndex, nvmlDeviceGetUtilizationRates, nvmlDeviceGetTemperature, NVML_TEMPERATURE_GPU, nvmlDeviceGetName
    nvmlInit()
    NVIDIA_AVAILABLE = True
except :
    NVIDIA_AVAILABLE = False
    print("No nvidia GPU found.")

def format_storage(value_gb):
    """Format storage values, converting to TB if >= 1000GB"""
    if value_gb >= 1000:
        return f"{value_gb / 1000:.1f}TB"
    return f"{value_gb}GB"

def get_disk_info():
    total = 0
    used = 0

    for d in psutil.disk_partitions(all=True): 
        if 'devfs' in d.opts or 'autofs' in d.opts: 
            continue
        try:
            usage = psutil.disk_usage(d.mountpoint)
            total += usage.total
            used += usage.used
        except PermissionError:
            continue

    total_gb = total // (1024**3)
    used_gb = used // (1024**3)
    root_usage = psutil.disk_usage('/').percent

    return total_gb, used_gb, root_usage


def get_system_info(cpu_name,gpu_name, log_file):
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
        disk_total, disk_used, disk_usage = get_disk_info()

        # Get GPU info
        gpu_usage = 0
        gpu_temp = None
        gpu_name = gpu_name 

        if NVIDIA_AVAILABLE:
            try:
                handle = nvmlDeviceGetHandleByIndex(0)
                gpu_usage = nvmlDeviceGetUtilizationRates(handle).gpu
                gpu_temp = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
                gpu_name = nvmlDeviceGetName(handle) 
            except Exception as e:
                if log_file != None:
                    with open(log_file, "a") as log:
                        log.write(f"{time.ctime()} - Error getting NVIDIA GPU data: {str(e)}\n")
        # Get CPU temperature
        cpu_temp = None
        try:
            temps = psutil.sensors_temperatures()
            if "coretemp" in temps:
                cpu_temp = sum(t.current for t in temps["coretemp"]) / len(temps["coretemp"])
        except:
            pass

        # Format values
        cpu_info = cpu_name  + " " + f"{cpu_count}c/{cpu_threads}t"
        ram_info = f"{format_storage(ram_used)} / {format_storage(ram_total)}"
        disk_info = f"{format_storage(disk_used)} / {format_storage(disk_total)}"
        battery_left = None
        is_charging = None
        if(psutil.sensors_battery() != None):
            battery_left = psutil.sensors_battery().percent
            is_charging = psutil.sensors_battery().power_plugged

        return {
            "cpuUsage": cpu_usage,
            "gpuUsage": gpu_usage,
            "ramUsage": ram_usage,
            "diskUsage": disk_usage,
            "battery": battery_left,
            "isCharging": is_charging,
            "os": platform.platform(),
            "cpu": cpu_info,
            "gpu": gpu_name,
            "ram": ram_info,
            "disk": disk_info,
            "cpuTemp": cpu_temp,
            "gpuTemp": gpu_temp
        }
    except Exception as e:
        with open(log_file, "a") as log:
            log.write(f"{time.ctime()} - Error in get_system_info: {str(e)}\n")
        return None
