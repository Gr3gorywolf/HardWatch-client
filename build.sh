pyinstaller --onefile --icon=icon.ico --noconsole --hidden-import socketio --hidden-import engineio client.py && cp icon.ico ./dist/icon.ico && cp ~config.json ./dist/~config.json
