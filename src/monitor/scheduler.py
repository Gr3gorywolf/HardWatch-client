import threading
import time
from config import APP_KEY, BACKEND_URL, ACTIONABLES, ERROR_LOG
from monitor.running_services import check_service_status
from transport.http_client import send_device_info, send_usages


def usages_thread_process():
    while True:
        try:
            response = send_usages()
            if response and response.status_code == 200:
                print("Usage data sent!")
            else:
                raise Exception(f"Failed to send device stats: {response.status_code if response else 'No response'}")

        except Exception as e:
            print(e)
            with open(ERROR_LOG, "a") as log:
                log.write(f"{time.ctime()} - {str(e)}\n")
        time.sleep(3)

def stats_tread_process():
    usage_thread_started = False
    while True:
        try:
            request = send_device_info()
            response = request.get("response")
            payload = request.get("payload")

            if response and response.status_code == 200:
                print("Device info sent!")
                if not usage_thread_started:
                    usage_thread_started = True
                    usage_thread = threading.Thread(target=usages_thread_process, name="send_usages", daemon=True)
                    usage_thread.start()
                time.sleep(60)
            else:
                raise Exception(f"Failed to send device info: {response.status_code if response else 'No response'}")

        except Exception as e:
            print(e)
            with open(ERROR_LOG, "a") as log:
                log.write(f"{time.ctime()} - {str(e)}\n")
        time.sleep(3)

def start_schedulers():
    thread = threading.Thread(target=stats_tread_process, name="send_stats", daemon=True)
    thread.start()