# Miner Scanner GUI

A Pygame GUI for Raspberry Pi that scans a LAN subnet for ASIC miners (Whatsminer, Antminer, etc.) and displays all miner data on a 3.5" TFT LCD 480x320 SPI touchscreen. Supports touch pen interaction.

## Features

- Scan LAN IP range for ASIC miners
- Whatsminer support (50+ models)
- Antminer and other pyasic-supported miners
- Display all miner data: IP, hostname, model, hashrate, wattage, temp, fans, workers, pools, errors
- Touch-friendly UI (44x44 px minimum targets) for resistive touch + touch pen
- Scrollable miner list and detail view

## Requirements

- Python 3.10+
- Raspberry Pi with 3.5" TFT LCD 480x320 SPI display (ILI9486/ILI9488 or compatible)
- Resistive touch overlay with touch pen

## Installation

### One-line install (Raspberry Pi / Linux)

Install via curl — runs automatically on every reboot:

```bash
curl -sSL https://raw.githubusercontent.com/miladkhalafi/pi-miner-scanner/main/installer/install.sh | sudo bash
```

**Installer web page** (Docker): Run the installer image to serve a web page with the install command:

```bash
# Image: ghcr.io/miladkhalafi/pi-miner-scanner-installer (from GitHub Actions)
docker run -p 8080:80 ghcr.io/miladkhalafi/pi-miner-scanner-installer:latest
```

Then visit `http://localhost:8080` and use the curl command shown there.

### Manual install

```bash
pip install -r requirements.txt
```

## Display Setup (3.5" TFT LCD SPI + Touch Pen)

### Enable SPI

```bash
sudo raspi-config
# Interface Options → SPI → Enable
```

### Display Driver (choose one)

**LCD-show** (easiest):
```bash
git clone https://github.com/goodtft/LCD-show.git
chmod -R 755 LCD-show
cd LCD-show
sudo ./LCD35-show
# Reboots automatically
```

**Waveshare/Elecrow**: Use vendor scripts (e.g., `LCD35-show` or `LCD35B-show` for 480x320).

**Manual fbtft**: Add device tree overlay in `/boot/config.txt` for ILI9486/ILI9488.

### Touch Calibration

If touch coordinates are offset, calibrate with:
```bash
sudo apt install xinput-calibrator
xinput_calibrator
```

## Running

### On Raspberry Pi (SPI TFT as display)

```bash
SDL_FBDEV=/dev/fb0 SDL_VIDEODRIVER=fbcon python3 main.py
```

Or use a launch script:

```bash
#!/bin/bash
export SDL_FBDEV=/dev/fb0
export SDL_VIDEODRIVER=fbcon
python3 /path/to/miner-scanner/main.py
```

### On Desktop (development)

```bash
python3 main.py
```

Runs in a normal window for testing.

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `MINER_SCANNER_SUBNET` | Auto-detected `/24` | IP range to scan (e.g., `192.168.1.0/24`) |
| `MINER_SCANNER_WHATSMINER_PASSWORD` | `admin` | Whatsminer API password |

## Wiring (typical 3.5" SPI TFT)

- RST → GPIO 24
- D/C → GPIO 25
- CS → CE0
- MOSI, SCLK, GND, 3.3V
- Touch: separate SPI or I2C (model-dependent)

## UI Flow

1. **Home**: Tap "Scan" to discover miners; "View (N)" appears when scan completes
2. **Miner List**: Scrollable list (IP | Model | TH/s); tap row for details
3. **Detail**: All miner data with scroll; tap "Back" to return

## Systemd Service (optional)

```ini
[Unit]
Description=Miner Scanner GUI
After=graphical.target

[Service]
Type=simple
Environment=SDL_FBDEV=/dev/fb0
Environment=SDL_VIDEODRIVER=fbcon
ExecStart=/usr/bin/python3 /home/pi/miner-scanner/main.py
Restart=on-failure
User=pi

[Install]
WantedBy=graphical.target
```
