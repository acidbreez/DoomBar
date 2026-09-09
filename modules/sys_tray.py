import os

from gi.repository import Gio

class sys_tray():
    def __init__(self, bus):
        super().__init__()

        tray_proxy = Gio.DBusProxy.new_sync(
            bus,
            Gio.DBusProxyFlags.NONE,
            None,
            "org.kde.StatusNotifierWatcher",
            "/StatusNotifierWatcher",
            "org.kde.StatusNotifierWatcher",
            None
        )

        