#!/bin/bash
set -e

echo "Starting Bluetooth Battery Indicator Universal Installer..."

# 1. Detect package manager and install system dependencies
if command -v apt >/dev/null 2>&1; then
    echo "Detected Debian/Ubuntu (apt). Installing dependencies..."
    sudo apt update
    sudo apt install -y python3 python3-venv python3-pip python3-dbus libglib2.0-bin
elif command -v dnf >/dev/null 2>&1; then
    echo "Detected Fedora (dnf). Installing dependencies..."
    sudo dnf install -y python3 python3-pip python3-dbus glib2
elif command -v pacman >/dev/null 2>&1; then
    echo "Detected Arch Linux (pacman). Installing dependencies..."
    sudo pacman -Syu --noconfirm python python-pip python-dbus glib2
elif command -v zypper >/dev/null 2>&1; then
    echo "Detected openSUSE (zypper). Installing dependencies..."
    sudo zypper install -y python3 python3-pip python3-dbus-python glib2-tools
else
    echo "Unsupported package manager. Please install Python 3, pip, python3-dbus, and glib2 manually."
    exit 1
fi

# 2. Define installation directories
INSTALL_DIR="$HOME/.local/share/bluetooth-battery-indicator"
AUTOSTART_DIR="$HOME/.config/autostart"
APP_DIR="$HOME/.local/share/applications"

echo "Creating directories..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$AUTOSTART_DIR"
mkdir -p "$APP_DIR"

# 3. Copy files to the user's local application directory
echo "Copying files..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR/indicator.py" "$INSTALL_DIR/"

if [ -f "$SCRIPT_DIR/batterylow.mp3" ]; then
    cp "$SCRIPT_DIR/batterylow.mp3" "$INSTALL_DIR/"
fi

# 4. Set up Python Virtual Environment (cross-distro safe python packaging)
echo "Setting up Python Virtual Environment..."
cd "$INSTALL_DIR"
# Use system-site-packages so it can access the system's python-dbus bindings
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install --upgrade pip
pip install pystray Pillow

# 5. Create startup scripts and desktop shortcuts
echo "Creating startup scripts and desktop shortcuts..."
cat << 'EOF' > "$INSTALL_DIR/run.sh"
#!/bin/bash
cd "$HOME/.local/share/bluetooth-battery-indicator"
source venv/bin/activate
exec python3 indicator.py
EOF
chmod +x "$INSTALL_DIR/run.sh"

cat << EOF > "$APP_DIR/bluetooth-battery-indicator.desktop"
[Desktop Entry]
Name=Bluetooth Battery Indicator
Comment=System tray icon for Bluetooth battery level
Exec=$INSTALL_DIR/run.sh
Icon=bluetooth
Terminal=false
Type=Application
Categories=Utility;
StartupNotify=false
EOF

# Make it start on boot
cp "$APP_DIR/bluetooth-battery-indicator.desktop" "$AUTOSTART_DIR/"

echo "============================================================"
echo "Installation complete! "
echo "The indicator will start automatically on your next login."
echo "Starting it now for you..."
echo "============================================================"

# Kill any existing instance to prevent duplicates, then run the new one
pkill -f "indicator.py" || true
"$INSTALL_DIR/run.sh" &
