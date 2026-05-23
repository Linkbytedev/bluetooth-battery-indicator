import dbus
bus = dbus.SystemBus()
manager = dbus.Interface(bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")
objects = manager.GetManagedObjects()

for path, interfaces in objects.items():
    if "org.bluez.Battery1" in interfaces:
        battery = interfaces["org.bluez.Battery1"]
        print(f"Device: {path}")
        print(f"Battery %: {battery.get('Percentage', 'Unknown')}")
    if "org.bluez.Device1" in interfaces:
        device = interfaces["org.bluez.Device1"]
        print(f"Found Device: {device.get('Name', path)} - Connected: {device.get('Connected')}")
