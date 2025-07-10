import os
import socketio

from config import ACTIONABLES, BACKEND_URL, APP_KEY, DEVICE_ID
from tray.notifications import show_notification


sio = socketio.Client() 
def start_socket_client():
    ## Socket IO setup
    @sio.event
    def connect():
        show_notification("HardWatch", "HardWatch Client connected successfully!, See the tray icon for options.")
        print("Connected to server")

    @sio.event
    def disconnect():
        print("Disconnected from server")
        show_notification("HardWatch", "Disconnected from server")

    @sio.on("execute-action")
    def handle_action(data):
        action_name = data["action"]
        print(f"Executing action: {action_name}")

        # Buscar la acción en la lista de `actionables`
        action_command = None
        for item in ACTIONABLES:
            if item["name"].lower() == action_name.lower():
                action_command = item["action"]
                break

        if action_command:
            print(f"Running command: {action_command}")
            os.system(action_command)
        else:
            print(f"Action '{action_name}' not found in actionables")

    try:
        sio.connect(BACKEND_URL, auth={"appKey": APP_KEY, "id": DEVICE_ID})
    except:
        print("Error connecting to socket server")
        show_notification("HardWatch", "Failed to connect to server")
        pass