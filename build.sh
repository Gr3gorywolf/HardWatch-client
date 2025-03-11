pyinstaller --onefile --icon=icon.ico --hidden-import socketio client.py && cp icon.ico ./dist/icon.ico && cp ~config.json ./dist/~config.json
