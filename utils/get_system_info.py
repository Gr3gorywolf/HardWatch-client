import platform
import time
import psutil
try:
    from pynvml import nvmlInit, nvmlShutdown, nvmlDeviceGetHandleByIndex, nvmlDeviceGetUtilizationRates, nvmlDeviceGetTemperature, NVML_TEMPERATURE_GPU, nvmlDeviceGetName
    nvmlInit()
    NVIDIA_AVAILABLE = True
except :
    NVIDIA_AVAILABLE = False
    print("NVML no disponible en este entorno")

def format_storage(value_gb):
    """Format storage values, converting to TB if >= 1000GB"""
    if value_gb >= 1000:
        return f"{value_gb / 1000:.1f}TB"
    return f"{value_gb}GB"


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
        disks = psutil.disk_partitions()
        disk_total = sum(psutil.disk_usage(d.mountpoint).total for d in disks) // (1024**3)  # GB
        disk_used = sum(psutil.disk_usage(d.mountpoint).used for d in disks) // (1024**3)  # GB
        disk_usage = psutil.disk_usage('/').percent

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

        return {
            "cpuUsage": cpu_usage,
            "gpuUsage": gpu_usage,
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
        with open(log_file, "a") as log:
            log.write(f"{time.ctime()} - Error in get_system_info: {str(e)}\n")
        return None
