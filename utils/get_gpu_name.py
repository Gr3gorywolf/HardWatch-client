import subprocess
import platform
def get_gpu_name():
    try:
        os_type = platform.system()
        if os_type == "Linux":
                gpu_info = subprocess.check_output(["lspci", "|", "grep", "-i", "vga"], stderr=subprocess.STDOUT)
                gpu_name = gpu_info.decode().split(":")[2].strip()  # Extrae el nombre de la GPU
                return gpu_name

        elif os_type == "Darwin":
                gpu_info = subprocess.check_output(["system_profiler", "SPDisplaysDataType"], stderr=subprocess.STDOUT)
                gpu_name = gpu_info.decode().split("Chipset Model:")[1].split("\n")[0].strip()
                return gpu_name

        elif os_type == "Windows":
                gpu_info = subprocess.check_output(
                    ["powershell", "-Command", "Get-WmiObject Win32_VideoController | Select-Object -ExpandProperty Caption"],
                    stderr=subprocess.STDOUT
                ).decode().strip()
                return gpu_info

        else:
            return "Unknown GPU"
    except:
        return "Unknown GPU"