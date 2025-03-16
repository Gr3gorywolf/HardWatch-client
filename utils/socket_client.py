import os
import socketio


sio = socketio.Client() 
def start_socket_client(appKey, deviceId, backendUrl, actionables):
    ## Socket IO setup
    @sio.event
    def connect():
        print("Connected to server")

    @sio.event
    def disconnect():
        print("Disconnected from server")

    @sio.on("execute-action")
    def handle_action(data):
        action_name = data["action"]
        print(f"Executing action: {action_name}")

        # Buscar la acción en la lista de `actionables`
        action_command = None
        for item in actionables:
            if item["name"].lower() == action_name.lower():
                action_command = item["action"]
                break

        if action_command:
            print(f"Running command: {action_command}")
            os.system(action_command)
        else:
            print(f"Action '{action_name}' not found in actionables")

    try:
        sio.connect(backendUrl, auth={"appKey": appKey, "id": deviceId})
    except:
        print("Error connecting to socket server")
        pass