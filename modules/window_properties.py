import gi 

gi.require_version("Gtk", "4.0") # refer to gtk4
gi.require_version("Gdk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")

from gi.repository import Gtk4LayerShell

class WindowProperties:
    def WindowProperties_init(self, window, monitor):
        # Create wayland desktop layer
        Gtk4LayerShell.init_for_window(window)
        Gtk4LayerShell.set_layer(window, Gtk4LayerShell.Layer.TOP)
        Gtk4LayerShell.set_monitor(window, monitor)

        # Anchor window to specific location
        Gtk4LayerShell.set_anchor(window, Gtk4LayerShell.Edge.BOTTOM, True)
        Gtk4LayerShell.set_anchor(window, Gtk4LayerShell.Edge.LEFT, True)
        Gtk4LayerShell.set_anchor(window, Gtk4LayerShell.Edge.RIGHT, True)

        # The taskbar itself does not need keyboard focus.
        Gtk4LayerShell.set_keyboard_mode(window, Gtk4LayerShell.KeyboardMode.NONE)

        # Reserve space at the bottom of the screen for the bar
        Gtk4LayerShell.auto_exclusive_zone_enable(window)
    
        # Give layer surface an unique namespace
        Gtk4LayerShell.set_namespace(window, "dooms-taskbar")

        window.set_default_size(-1, 1)

        print(f"Window properties are loaded")

window_properties = WindowProperties()