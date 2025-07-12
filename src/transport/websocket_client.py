import os
import socketio
import config
from tray.notifications import show_notification


sio = socketio.Client()


def stop_socket_client():
    sio.disconnect()
    print("Socket client disconnected")


def start_socket_client(on_connect: callable = None, on_disconnect: callable = None):
    ## Socket IO setup
    @sio.event
    def connect():
        show_notification(
            "HardWatch",
            "HardWatch Client connected successfully!, See the tray icon for options.",
        )
        print("Connected to server")
        if on_connect is not None:
            on_connect()

    @sio.event
    def disconnect():
        print("Disconnected from server")
        show_notification("HardWatch", "Disconnected from server")
        if on_disconnect is not None:
            on_disconnect()

    @sio.on("execute-action")
    def handle_action(data):
        action_name = data["action"]
        print(f"Executing action: {action_name}")

        # Buscar la acción en la lista de `actionables`
        action_command = None
        for item in config.ACTIONABLES:
            if item["name"].lower() == action_name.lower():
                action_command = item["action"]
                break

        if action_command:
            print(f"Running command: {action_command}")
            os.system(action_command)
        else:
            print(f"Action '{action_name}' not found in actionables")

    try:
        sio.connect(config.BACKEND_URL, auth={"appKey": config.APP_KEY, "id": config.DEVICE_ID})
    except:
        print("Error connecting to socket server")
        show_notification("HardWatch", "Failed to connect to server")
        pass
