#!/bin/bash
set -e

# Miner Scanner Installer
# Run with: curl -sSL https://YOUR_SERVER/install.sh | bash
# Or from GitHub: curl -sSL https://raw.githubusercontent.com/OWNER/miner-scanner/main/installer/install.sh | bash

GITHUB_REPO="${GITHUB_REPO:-@@GITHUB_REPO@@}"
INSTALL_DIR="${INSTALL_DIR:-/opt/miner-scanner}"
SERVICE_USER="${SERVICE_USER:-root}"

echo "==> Miner Scanner Installer"
echo "==> Repository: $GITHUB_REPO"
echo "==> Install directory: $INSTALL_DIR"
echo ""

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
  echo "This script requires root. Run with: curl -sSL ... | sudo bash"
  echo "Or: curl -sSL ... | sudo bash"
  exit 1
fi

# Detect platform
if [ -f /etc/os-release ]; then
  . /etc/os-release
  OS=$ID
else
  echo "Cannot detect OS"
  exit 1
fi

echo "==> Detected OS: $OS"
echo "==> Installing dependencies..."

# Install Python3, pip, git
case "$OS" in
  debian|ubuntu|raspbian)
    apt-get update -qq
    apt-get install -y -qq python3 python3-pip python3-venv git
    ;;
  fedora|rhel|centos)
    dnf install -y -q python3 python3-pip git 2>/dev/null || yum install -y -q python3 python3-pip git
    ;;
  arch)
    pacman -Sy --noconfirm python python-pip git
    ;;
  *)
    echo "Unsupported OS: $OS. Please install Python 3.10+, pip, and git manually."
    exit 1
    ;;
esac

echo "==> Cloning miner-scanner..."
mkdir -p "$(dirname "$INSTALL_DIR")"
if [ -d "$INSTALL_DIR/.git" ]; then
  cd "$INSTALL_DIR"
  git fetch --all
  git pull
else
  rm -rf "$INSTALL_DIR"
  git clone "$GITHUB_REPO" "$INSTALL_DIR"
  cd "$INSTALL_DIR"
fi

echo "==> Installing Python dependencies..."
python3 -m pip install --break-system-packages -r requirements.txt 2>/dev/null || \
  python3 -m pip install -r requirements.txt

echo "==> Creating systemd service..."
cat > /etc/systemd/system/miner-scanner.service << EOF
[Unit]
Description=Miner Scanner GUI
After=network-online.target graphical.target
Wants=network-online.target

[Service]
Type=simple
Environment=SDL_FBDEV=/dev/fb0
Environment=SDL_VIDEODRIVER=fbcon
Environment=DISPLAY=:0
ExecStart=/usr/bin/python3 $INSTALL_DIR/main.py
Restart=on-failure
RestartSec=10
User=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR

[Install]
WantedBy=multi-user.target
EOF

echo "==> Enabling and starting miner-scanner service..."
systemctl daemon-reload
systemctl enable miner-scanner.service
systemctl start miner-scanner.service

echo ""
echo "==> Installation complete!"
echo "==> Miner Scanner is installed at $INSTALL_DIR"
echo "==> Service is enabled and will start automatically on reboot."
echo ""
echo "Useful commands:"
echo "  sudo systemctl status miner-scanner   # Check status"
echo "  sudo systemctl restart miner-scanner  # Restart"
echo "  sudo systemctl stop miner-scanner     # Stop"
echo "  sudo journalctl -u miner-scanner -f   # View logs"
echo ""
