import time
import threading
import dbus
from PIL import Image, ImageDraw, ImageFont
import pystray
import subprocess
import urllib.request
import json
import os
import threading

CURRENT_VERSION = "1.0.0"
GITHUB_REPO = "USERNAME/REPO" # Replace with your GitHub username/repository


def get_bluetooth_batteries():
    devices_info = []
    try:
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object('org.bluez', '/'), 'org.freedesktop.DBus.ObjectManager')
        objects = manager.GetManagedObjects()

        for path, interfaces in objects.items():
            if 'org.bluez.Device1' in interfaces and 'org.bluez.Battery1' in interfaces:
                device = interfaces['org.bluez.Device1']
                battery = interfaces['org.bluez.Battery1']
                
                connected = device.get('Connected')
                if connected:
                    name = str(device.get('Name', 'Unknown Device'))
                    percentage = int(battery.get('Percentage', 0))
                    devices_info.append({'name': name, 'percentage': percentage})
    except Exception as e:
        print(f"Error querying dbus: {e}")
        
    return devices_info

def check_for_updates(icon, item):
    def run_update():
        try:
            # Send notification that update check is starting
            subprocess.Popen(['notify-send', 'Bluetooth Battery Indicator', 'Checking for updates...'])
            
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
            latest_version = data.get("tag_name", "").lstrip("v")
            if latest_version and latest_version != CURRENT_VERSION:
                # Find the .deb asset
                deb_url = None
                for asset in data.get("assets", []):
                    if asset["name"].endswith(".deb"):
                        deb_url = asset["browser_download_url"]
                        break
                        
                if deb_url:
                    subprocess.Popen(['notify-send', 'Bluetooth Battery Indicator', f'Downloading update v{latest_version}...'])
                    deb_path = "/tmp/bluetooth-battery-indicator-update.deb"
                    urllib.request.urlretrieve(deb_url, deb_path)
                    
                    subprocess.Popen(['notify-send', 'Bluetooth Battery Indicator', 'Installing update. Please enter your password if prompted.'])
                    # pkexec runs dpkg as root with a GUI password prompt
                    subprocess.Popen(['pkexec', 'dpkg', '-i', deb_path])
                else:
                    subprocess.Popen(['notify-send', 'Bluetooth Battery Indicator', 'No .deb file found in the latest release.'])
            else:
                subprocess.Popen(['notify-send', 'Bluetooth Battery Indicator', 'You are already up to date!'])
        except Exception as e:
            subprocess.Popen(['notify-send', 'Bluetooth Battery Indicator', f'Update failed: {e}'])
            
    threading.Thread(target=run_update, daemon=True).start()

def create_icon_image(percentage, is_connected):
    # Create a 64x64 image
    img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if not is_connected:
        # Draw a disconnected/empty battery outline
        draw.rectangle([10, 20, 54, 44], outline="gray", width=4)
        draw.rectangle([54, 26, 58, 38], fill="gray")
        draw.line([15, 15, 49, 49], fill="gray", width=4)
        return img

    # Outline
    draw.rectangle([10, 20, 54, 44], outline="white", width=4)
    # Tip
    draw.rectangle([54, 26, 58, 38], fill="white")
    
    # Fill based on percentage
    if percentage > 0:
        fill_width = int((percentage / 100.0) * 40)
        fill_color = "green" if percentage > 20 else "red"
        draw.rectangle([14, 24, 14 + fill_width, 40], fill=fill_color)
        
    return img

def update_loop(icon):
    notified_devices = set()
    while True:
        try:
            batteries = get_bluetooth_batteries()
            if batteries:
                # Show the lowest battery percentage if multiple
                batteries.sort(key=lambda x: x['percentage'])
                lowest = batteries[0]
                
                # Update icon
                icon.icon = create_icon_image(lowest['percentage'], True)
                
                # Update menu
                menu_items = []
                for b in batteries:
                    menu_items.append(pystray.MenuItem(f"{b['name']}: {b['percentage']}%", lambda *args: None))
                    
                    # Battery low notification logic
                    if b['percentage'] <= 20 and b['name'] not in notified_devices:
                        try:
                            subprocess.Popen(['notify-send', '-u', 'critical', 'Bluetooth Battery Low', f"{b['name']} is at {b['percentage']}%"])
                            subprocess.Popen(['gio', 'play', '/usr/share/bluetooth-battery-indicator/we-o_rd35hn_mbnylqzn15-battery-490734.mp3'])
                        except Exception:
                            pass
                        notified_devices.add(b['name'])
                    elif b['percentage'] > 20 and b['name'] in notified_devices:
                        notified_devices.remove(b['name'])
                        
                menu_items.append(pystray.Menu.SEPARATOR)
                menu_items.append(pystray.MenuItem("Check for Updates", check_for_updates))
                menu_items.append(pystray.MenuItem("Exit", lambda *args: icon.stop()))
                
                icon.menu = pystray.Menu(*menu_items)
                icon.title = f"{lowest['name']}: {lowest['percentage']}%"
            else:
                icon.icon = create_icon_image(0, False)
                icon.menu = pystray.Menu(
                    pystray.MenuItem("No devices connected", lambda *args: None),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem("Check for Updates", check_for_updates),
                    pystray.MenuItem("Exit", lambda *args: icon.stop())
                )
                icon.title = "Bluetooth Battery: Disconnected"
                
        except Exception as e:
            print(f"Update error: {e}")
            
        time.sleep(10)

def main():
    icon = pystray.Icon("bluetooth-battery")
    icon.icon = create_icon_image(0, False)
    icon.menu = pystray.Menu(
        pystray.MenuItem("Starting...", lambda *args: None),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Check for Updates", check_for_updates),
        pystray.MenuItem("Exit", lambda *args: icon.stop())
    )
    icon.title = "Bluetooth Battery"
    
    # Run update loop in background
    thread = threading.Thread(target=update_loop, args=(icon,), daemon=True)
    thread.start()
    
    # This blocks until icon.stop() is called
    icon.run()

if __name__ == "__main__":
    main()
