import json
import os
import sys
import threading
import time
import webview
import multiprocessing

import config
from monitor.scheduler import start_schedulers, stop_schedulers
from transport.websocket_client import start_socket_client, stop_socket_client
from tray.notifications import show_notification
from utils.js_api import JsApi

Process = multiprocessing.Process
queue = multiprocessing.Queue()

HTML_PATH = os.path.abspath("web/config/index.html")


def on_save_main(data: dict):
    print("restart called")
    with open("config.json", "w") as f:
        json.dump(data, f, indent=4)

    show_notification("HardWatch", "Reloading services…")
    config.load_config()
    stop_socket_client()
    stop_schedulers()
    start_schedulers()
    start_socket_client()


# Listener en un hilo daemon
def queue_listener(q):
    while True:
        new_conf = q.get()
        if new_conf is None:
            break
        on_save_main(new_conf)


threading.Thread(target=queue_listener, args=(queue,), daemon=True).start()


def show_config_setup(initial_conf, q):
    api = JsApi(json_data=initial_conf, on_save=lambda data: q.put(data))
    webview.create_window(
        "Device Configuration",
        HTML_PATH,
        width=800,
        height=600,
        js_api=api,
        resizable=False,
    )
    webview.start()


config_proc: multiprocessing.Process = None


def open_config_setup():
    global config_proc, queue, Process
    if config_proc is None or not config_proc.is_alive():
        config_proc = Process(
            target=show_config_setup,
            args=(config.CONFIG, queue),
            daemon=True,
            name="config_setup_process",
        )
        config_proc.start()
