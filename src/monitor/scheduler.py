import threading
import time
from transport.http_client import send_device_info, send_usages

schedulers_thread: threading.Thread = None
RETRY_INTERVAL = 30
stop_event = threading.Event()

def handle_retry(st_event:threading.Event):
    print("Failed to send data, retrying in 30 seconds...")
    st_event.wait(RETRY_INTERVAL)

def usages_thread_process(st_event:threading.Event):
    while not st_event.wait(3):
        try:
            response = send_usages()
            if response and response.status_code == 200:
                print("Usage data sent!")
            else:
                raise Exception(
                    f"Failed to send device stats: {response.status_code if response else 'No response'}"
                )

        except Exception as e:
            print(e)
            handle_retry(st_event)


def stats_tread_process(st_event:threading.Event):
    usage_thread_started = False
    while not st_event.wait(10):
        try:
            response = send_device_info()

            if response and response.status_code == 200:
                print("Device info sent!")
                if not usage_thread_started:
                    usage_thread_started = True
                    usage_thread = threading.Thread(
                        target=usages_thread_process, name="send_usages", daemon=True,
                        args=(st_event,)
                    )
                    usage_thread.start()
                st_event.wait(60)
            else:
                raise Exception(
                    f"Failed to send device info: {response.status_code if response else 'No response'}"
                )

        except Exception as e:
            print(e)
            handle_retry(st_event)


def stop_schedulers():
    global stop_event
    global schedulers_thread
    if schedulers_thread is None:
        print("No schedulers to stop")
        return

    print("Stopping schedulers...")
    stop_event.set()
    schedulers_thread.join(timeout=1)
    schedulers_thread = None
    print("Schedulers stopped")


def start_schedulers():
    global stop_event
    global schedulers_thread
    if schedulers_thread and schedulers_thread.is_alive():
        print("Schedulers already running")
        return
    stop_event.clear() 
    schedulers_thread = threading.Thread(
        target=stats_tread_process, name="send_stats", daemon=True,
        args=(stop_event,)
    )
    print(schedulers_thread)
    schedulers_thread.start()
