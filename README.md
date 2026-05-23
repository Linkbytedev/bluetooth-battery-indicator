# Bluetooth Battery Indicator

A lightweight, native system tray application for Linux that displays the real-time battery percentage of your connected Bluetooth devices (like headphones, earbuds, and mice). 

Designed to work across **ALL Linux distributions** (Ubuntu, Fedora, Arch Linux, openSUSE, etc.), it sits quietly in your tray, gives you low-battery sound alerts, and automatically updates itself!

## Features
- **Real-Time Visuals**: The tray icon changes dynamically based on your device's battery level.
- **Detailed Menu**: Click the icon to see the exact battery percentage and name of the connected device.
- **Low Battery Alerts**: Get a native desktop notification and a sound alert when your battery drops to 20% or lower.
- **Auto-Updating**: Features a built-in updater (via GitHub Releases).

---

## How to Install (Universal Method)

You can install this app on any Linux distribution (Ubuntu, Arch Linux, Fedora, Linux Mint, etc.) using the universal install script!

### The Quick Way (One-Line Install)
Open your terminal and paste this command to download and install the app automatically:

```bash
git clone https://github.com/Linkbytedev/bluetooth-battery-indicator.git && cd bluetooth-battery-indicator && chmod +x install.sh && ./install.sh
```

### The Manual Way
1. Download or clone this repository to your computer.
2. Open your terminal inside the downloaded folder.
3. Run the installer script:

```bash
chmod +x install.sh
./install.sh
```

The script will automatically:
- Detect your OS (Debian/Fedora/Arch/openSUSE).
- Use your system's package manager (`apt`, `dnf`, `pacman`, `zypper`) to install the required dependencies safely.
- Install the app to your `~/.local/share` folder.
- Add a shortcut to your application launcher and set it to run on boot!
