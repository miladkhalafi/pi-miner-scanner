"""Configuration for IP range, Whatsminer password, and display."""

import os
import socket


def get_default_subnet() -> str:
    """Auto-detect subnet from Pi's interface (e.g., 192.168.1.x -> /24)."""
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        if ip and ip != "127.0.0.1":
            parts = ip.rsplit(".", 1)
            if len(parts) == 2:
                return f"{parts[0]}.0/24"
    except (socket.gaierror, socket.herror, OSError):
        pass
    return "192.168.1.0/24"


# IP range for scanning; override via env MINER_SCANNER_SUBNET
SUBNET = os.environ.get("MINER_SCANNER_SUBNET", get_default_subnet())

# Whatsminer API password; override via env MINER_SCANNER_WHATSMINER_PASSWORD
WHATSMINER_PASSWORD = os.environ.get("MINER_SCANNER_WHATSMINER_PASSWORD", "admin")

# Display dimensions for 3.5" TFT LCD
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 320

# Minimum touch target size (px) for touch pen
MIN_TOUCH_TARGET = 44

# Web server port for scan results (default 80; port 80 requires root or setcap)
WEB_PORT = int(os.environ.get("MINER_SCANNER_WEB_PORT", "80"))
