#!/usr/bin/python3

#import python modules
import os

# import config files
from configs.gtk_layer_shell import gtk_layer_shell

# load config files
gtk_layer_shell.gtk_shell()

# import DoomBar Modules
from modules.window_properties import window_properties
from modules.start_menu import StartMenu
from modules.events import Events
from modules.clock import MyClock
from modules.control_center import ControlCenter
from modules.battery import Battery
from modules.media_player import MediaPlayer

# import gtk modules
import gi

from gi.repository import (
    Gdk,
    GdkPixbuf,
    Gio,
    GLib,
    Gtk,
    Gtk4LayerShell,
)

# Create  setting file locations
BATTERY = "/sys/class/power_supply/BAT0/capacity"
AC = "/sys/class/power_supply/AC0/online"
XDG_RUNTIME = os.environ.get("XDG_RUNTIME_DIR")
HYPR_SIG = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
HYPR_SOCK = f"{XDG_RUNTIME}/hypr/{HYPR_SIG}/.socket.sock"
HYPR_SOCK2 = f"{XDG_RUNTIME}/hypr/{HYPR_SIG}/.socket2.sock"

# Config file locations
CONFIG = os.path.expanduser("~/.config/DoomBar/")
APP_BUTTON = (f"{CONFIG}theme/gentoo/start.svg")
CC_BUTTON = (f"{CONFIG}theme/gentoo/settings.png")
CSS_STYLE = (f"{CONFIG}theme/gentoo/style.css")

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, monitor, **kwargs):
        super().__init__(**kwargs, title="GTK-TaskBar")

        # start loading dbus
        self.bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)

        #ctrl_dbus = ControlCenter(self.bus)
        self.media_player = MediaPlayer(self.bus)

        # Window Properties
        window_properties.WindowProperties_init(self, monitor)

        self.guiLayout()

        self.clock = MyClock(self.clock_button)
        self.battery = Battery(self.battery_label, BATTERY, AC)
        self.control = ControlCenter(self.control_center, self.bus)
        self.workspace_box = Events(self.ws_box, HYPR_SOCK, HYPR_SOCK2)

    def guiLayout(self):
    
        start_image = Gtk.Image.new_from_file(APP_BUTTON)
        cc_image = Gtk.Image.new_from_file(CC_BUTTON)

        # create window 
        main_window = Gtk.CenterBox()

        # create containers
        self.start_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        clock_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        end_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    
        system_tray = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.ws_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.ws_box.add_css_class("workspace")

        # Labels
        self.battery_label = Gtk.Label()
        
        # Buttons
        start_button = Gtk.Button(child=start_image)
        start_button.set_has_frame(False)

        self.clock_button = Gtk.Button(label="")
        self.clock_button.set_has_frame(False)

        self.control_center = Gtk.Button(child=cc_image)
        self.control_center.set_has_frame(False)

        self.start_menu = StartMenu()
        self.start_menu.popover.set_parent(start_button)

        # Button Actions
        start_button.connect('clicked', self.on_start_click)

        # Build the widgets
        self.start_container.append(start_button)
        self.start_container.append(self.ws_box)
        #start_container.append(hypr)

        clock_container.append(self.clock_button)

        end_container.append(system_tray)
        end_container.append(self.battery_label)
        end_container.append(self.control_center)

        # Put the widgets together
        main_window.set_start_widget(self.start_container)
        main_window.set_center_widget(clock_container)
        main_window.set_end_widget(end_container)

        self.set_child(main_window)

        # set css settings
        main_window.add_css_class("main-window")
        self.start_container.add_css_class("start-container")
        clock_container.add_css_class("clock-container")
        end_container.add_css_class("end-container")
        system_tray.add_css_class("sys-tray")

    def on_start_click(self, button):
        self.start_menu.popover.popup()

def create_taskbar_for_monitor(app, monitor):
    # Create and display a taskbar for one monitor.
    window = MainWindow(
        application=app,
        monitor=monitor
    )

    # Keep track of the monitor/window pair.
    app.taskbars[monitor] = window

    geometry = monitor.get_geometry()
    print(
        f"Taskbar created for monitor: "
        f"{geometry.width}x{geometry.height}"
    )
    window.present()
    return window

def on_monitors_changed(monitors, position, removed, added, app):
    current_monitors = [
        monitors.get_item(i)
        for i in range(monitors.get_n_items())
    ]

    # Remove missing monitors.
    for monitor, window in list(app.taskbars.items()):
        if monitor not in current_monitors:
            print("Monitor removed")

            window.destroy()
            del app.taskbars[monitor]

    # Add new monitors.
    for monitor in current_monitors:
        if monitor not in app.taskbars:
            print("Monitor added")
            create_taskbar_for_monitor(app, monitor)

def on_activate(app):
    # Determining monitors
    display = Gdk.Display.get_default()
    # import css settings
        
    if os.path.exists(CSS_STYLE):
        css = Gtk.CssProvider()
        css.load_from_path(CSS_STYLE)
        Gtk.StyleContext.add_provider_for_display(display, css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    else:
        print(f"{CSS_STYLE} does not exist.")
        
    if display is None:
        print("Could not get default display")
        return

    if not Gtk4LayerShell.is_supported():
        print(
            "gtk4-layer-shell is not supported by this display/compositor."
        )
        print(
            "Make sure the application is running under Wayland "
            "with zwlr_layer_shell_v1 support."
        )
        return

    print(f"Display: {display.get_name()}")

    app.taskbars = {}

    monitors = display.get_monitors()

        # Create taskbars for currently connected monitors.
    for i in range(monitors.get_n_items()):
        monitor = monitors.get_item(i)

        geometry = monitor.get_geometry()

        print(
            f"Monitor {i}: "
            f"{geometry.width}x{geometry.height}"
        )

        create_taskbar_for_monitor(app, monitor)

    monitors.connect(
        "items-changed",
        on_monitors_changed,
        app
    )

if __name__ == "__main__":
    try:
        # Create a new application
        app = Gtk.Application(application_id="com.doom.TaskBar") # create application id
        app.connect("activate", on_activate)
        
        app.run(None)
    except OSError as e:
        print(f"There was an error: {e}")