pyinstaller --onefile --icon=icon.ico --add-data="icon.ico;." client.py && mv icon.ico dist/icon.ico && mv ~config.json dist/~config.json
