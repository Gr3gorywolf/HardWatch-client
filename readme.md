
<h4 style="text-align:center">
<img src="https://gr3gorywolf.github.io/HardWatch-server/assets/img/icon.png" height="300" width="300" alt="HardWatch Client Logo" />
</h4>

# HardWatch Client

[![GitHub release downloads](https://img.shields.io/github/downloads/Gr3gorywolf/HardWatch-client/latest/total?label=Total%20Downloads)](https://github.com/Gr3gorywolf/HardWatch-client/releases/latest)
[![Pipeline Status](https://img.shields.io/github/actions/workflow/status/Gr3gorywolf/HardWatch-client/main.yml?label=Pipeline%20Status)](https://github.com/Gr3gorywolf/HardWatch-client/actions)

## Overview

**HardWatch Client** is an application designed to monitor and collect real-time system performance metrics. It sends this data to the **HardWatch Server** and allows remote execution of commands via a web interface or the ZeppOS app.

### Features

- **Resource Monitoring**: Collects and tracks CPU, GPU, RAM, and disk usage.
- **Server Communication**: Sends performance data to a [HardWatch Server](https://github.com/Gr3gorywolf/HardWatch-server).
- **Discord Rich Presence Integration**: Displays system usage stats on Discord (configurable).
- **Remote Command Execution**: Executes predefined commands from the web app or ZeppOS app.


## Configuration

Before running the application, you need to set up a `config.json` file in the root directory. Below is the required structure:

```json
{
    "name": "<Device alias>",
    "appKey": "<Server app key>",
    "backendUrl": "<Server URL>",
    "type": "<Device type (desktop | laptop | handheld | server)>",
    "enable-discord-rpc": false,
    "actionables": [
        {
            "name": "<Actionable name>",
            "action": "<Actionable command>"
        }
    ]
}
```

### Configuration Parameters

| Parameter            | Description |
|----------------------|-------------|
| `name`              | Alias for identifying the device. |
| `appKey`            | Authentication key for connecting to the HardWatch server. |
| `backendUrl`        | URL of the HardWatch server. |
| `type`              | Specifies the type of device: `desktop`, `laptop`, `handheld`, or `server`. |
| `enable-discord-rpc`| Boolean value (`true` or `false`) to enable or disable Discord Rich Presence integration. |
| `actionables`       | List of commands that can be executed remotely. |
| `actionables.name`  | The name of the command. |
| `actionables.action`| The exact command to be executed. |

### Example Configuration

```json
{
    "name": "Gaming PC",
    "appKey": "my-secure-key",
    "backendUrl": "http://localhost:3000",
    "type": "desktop",
    "enable-discord-rpc": true,
    "actionables": [
        {
            "name": "Restart Explorer",
            "action": "taskkill /f /im explorer.exe && start explorer.exe"
        },
        {
            "name": "Clear Temp Files",
            "action": "del /q/f/s %TEMP%\*"
        }
    ]
}
```

## Usage

You can run the HardWatch Client in multiple ways:

### Using Precompiled Binaries
1. Download the appropriate binary from the [Releases page](https://github.com/Gr3gorywolf/HardWatch-client/releases/latest).
2. Run the executable for your platform (Windows, macOS, or Linux).

### Running with Docker
1. Clone the repository:
   ```sh
   git clone https://github.com/Gr3gorywolf/HardWatch-client.git
   cd HardWatch-client
   ```
2. Start the container:
   ```sh
   docker-compose up
   ```

### Running from Source
1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Run the application:
   ```sh
   python3 client.py
   ```

### General Workflow
1. The client will connect to the specified server and begin sending system performance data.
2. If Discord Rich Presence is enabled, hardware stats will be displayed in your Discord status.
3. Use the web app or ZeppOS app to send remote commands to the client.

## Contributing

If you want to contribute to HardWatch Client, feel free to fork the repository, create a feature branch, and submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Links

- **ZeppOs App**: [ZeppOs App](https://github.com/Gr3gorywolf/HardWatch-ZeppOs)
- **Server Repository**: [HardWatch Server](https://github.com/Gr3gorywolf/HardWatch-server)
- **Releases**: [Download Latest Version](https://github.com/Gr3gorywolf/HardWatch-client/releases/latest)

