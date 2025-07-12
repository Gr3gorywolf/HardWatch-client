import platform
import hashlib
import time
import requests
from monitor.collector import get_gpu_name, get_system_info, get_device_uuid
from monitor.running_services import check_service_status, parse_services, get_docker_services
import config
headers = {"appKey": config.APP_KEY}

def send_device_info():
    system_info = get_system_info(config.CPU_NAME, config.GPU_NAME, config.ERROR_LOG)
    parsed_services = parse_services(config.SERVICES)
    docker_services = get_docker_services()
    all_services = []
    for service in docker_services + parsed_services if config.USE_DOCKER_SERVICES else parsed_services:
        status = check_service_status(service)
        all_services.append(status)

    if system_info:
        payload = {
            "name": config.DEVICE_NAME,
            "id": config.DEVICE_ID,
            "type": config.DEVICE_TYPE,
            **system_info,
            "platform": platform.system(),
            "actionables": config.ACTIONABLES,
            "services": all_services,
        }
        print("Sending device info...")
        response = requests.post(f"{config.BACKEND_URL}/api/devices/send-stats-data", json=payload, headers=headers)
        return response

def send_usages():
            system_info = get_system_info(config.CPU_NAME, config.GPU_NAME, config.ERROR_LOG)
            if system_info:
                payload = {
                    "id": config.DEVICE_ID,
                    "battery": system_info.get("battery"),
                    "cpuUsage": system_info.get("cpuUsage"),
                    "diskUsage": system_info.get("diskUsage"),
                    "ramUsage": system_info.get("ramUsage"),
                    "gpuUsage": system_info.get("gpuUsage"),
                    "isCharging": system_info.get("isCharging"),
                    "ram": system_info.get("ram"),
                    "disk": system_info.get("disk"),
                    "cpuTemp": system_info.get("cpuTemp"),
                    "gpuTemp": system_info.get("gpuTemp"),
                }
                print("Sending usage data...")
                response = requests.post(f"{config.BACKEND_URL}/api/devices/send-device-usage", json=payload, headers=headers)
                if response.status_code == 404:
                    print("Resending device info...")
                    send_device_info()
                elif response.status_code != 200:
                    raise Exception(f"Usage post failed: {response.status_code}")
                return response