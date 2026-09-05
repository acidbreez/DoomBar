import os
import time

from datetime import (
    date,
    datetime,
)
import gi 

gi.require_version("Gtk", "4.0") # refer to gtk4
gi.require_version("Gdk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")

from gi.repository import Gtk, GLib

class MyClock:
    def __init__(self, button):
        try: 
            self.calendar = Gtk.Calendar()
            self.calendar.set_focusable(True)

            self.calendar.add_css_class("calendar")

            self.popover = Gtk.Popover()
            self.popover.set_has_arrow(False)
            self.popover.add_css_class("calendar-window")
            
            self.popover.set_child(self.calendar)
            self.popover.set_parent(button)

            self.digital_clock(button)

            button.set_label(self.currentTime)
            button.connect('clicked', self.on_clock_click)

            GLib.timeout_add_seconds(1, self.digital_clock, button)

            print("init done")
        except OSError as e:
            print(f"There was an error with your calendar: {e}")

    def digital_clock(self, button):
        try:
            self.currentTime = datetime.now().strftime("%I:%M:%S %p")
            button.set_label(self.currentTime)
            return True
        except OSError as e:
            print(f"There was an error with your clock: {e}")

    def on_clock_click(self, button):
        try:
            self.popover.popup()
        except OSError as e:
            print(f"There was an error with your calendar: {e}")