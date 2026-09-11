import os
import subprocess

from modules.media_player import MediaPlayer

from gi.repository import GdkPixbuf, Gio, Gtk, GLib
CONFIG = os.path.expanduser("~/.config/DoomBar/")

WIFION = (f"{CONFIG}theme/gentoo/gentoo_wifi.png")
WIFIOFF = (f"{CONFIG}theme/gentoo/gentoo_wifi_transparent.png")
BT_ON = (f"{CONFIG}theme/gentoo/gentoo_bt.png")
BT_OFF = (f"{CONFIG}theme/gentoo/gentoo_bt_transparent.png")

class ControlCenter:
    def __init__(self, button):
        super().__init__()
        bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        
        self.setPerc = 0
        self.displayBrightness()
        self.check_audio()

        # button images
        pixbuf_off = GdkPixbuf.Pixbuf.new_from_file_at_scale( filename=WIFIOFF, width=50, height=50, preserve_aspect_ratio=True)
        self.wifi_off = Gtk.Image.new_from_pixbuf(pixbuf_off)
        self.wifi_off.set_hexpand(True)
        self.wifi_off.set_vexpand(True)
        self.wifi_off.set_pixel_size(50)
    
        pixbuf_on = GdkPixbuf.Pixbuf.new_from_file_at_scale( filename=WIFION, width=50, height=50, preserve_aspect_ratio=True )
        self.wifi_on = Gtk.Image.new_from_pixbuf(pixbuf_on)
        self.wifi_on.set_hexpand(True)
        self.wifi_on.set_vexpand(True)
        self.wifi_on.set_pixel_size(50)

        pixbuf_bt_off = GdkPixbuf.Pixbuf.new_from_file_at_scale( filename=BT_OFF, width=50, height=50, preserve_aspect_ratio=True)
        self.bt_off = Gtk.Image.new_from_pixbuf(pixbuf_bt_off)
        self.bt_off.set_hexpand(True)
        self.bt_off.set_vexpand(True)
        self.bt_off.set_pixel_size(50)

        pixbuf_bt_on = GdkPixbuf.Pixbuf.new_from_file_at_scale( filename=BT_ON, width=50, height=50, preserve_aspect_ratio=True)
        self.bt_on = Gtk.Image.new_from_pixbuf(pixbuf_bt_on)
        self.bt_on.set_hexpand(True)
        self.bt_on.set_vexpand(True)
        self.bt_on.set_pixel_size(50)

        # create containers
        self.control_center = Gtk.Popover()
        control_center_grid = Gtk.Grid(column_spacing=0, row_spacing=0)
        brightness_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        audio_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        self.wifi_button = Gtk.Button(child=self.wifi_on)
        self.bt_button = Gtk.Button(child=self.bt_on)

        # create widgets
        self.media_player = MediaPlayer(bus)

        self.brightness = Gtk.Scale.new_with_range(
            orientation = Gtk.Orientation.HORIZONTAL,
            min = 1.0,
            max = 100.0,
            step = 1.0
        )

        self.volume = Gtk.Scale.new_with_range(
            orientation = Gtk.Orientation.HORIZONTAL,
            min = 0.0,
            max = 100.0,
            step = 1.0,
        )

        # Create Labels
        self.brightness_label = Gtk.Label(label=f"Display Brightness {int(self.perc)}%")
        self.volume_label = Gtk.Label(label=f"Volume: {int(self.setPerc)}%")

        # Window Properties
        self.control_center.set_has_arrow(False)
        self.control_center.set_parent(button)

        self.media_player.main.set_hexpand(True)
        self.media_player.main.set_vexpand(True)

        self.brightness_label.set_halign(Gtk.Align.FILL)
        self.brightness_label.set_hexpand(True)
        self.brightness_label.set_vexpand(False)

        self.brightness.set_halign(Gtk.Align.FILL)
        self.brightness.set_hexpand(True)
        self.brightness.set_vexpand(False)

        self.brightness.set_value(self.perc)
        self.brightness_signal_id = self.brightness.connect("value-changed", self.setBrightness)

        brightness_box.set_halign(Gtk.Align.FILL)
        brightness_box.append(self.brightness_label)
        brightness_box.append(self.brightness)
        
        audio_box.set_halign(Gtk.Align.FILL)
        audio_box.set_hexpand(True)
        audio_box.set_vexpand(False)

        self.volume_label.set_halign(Gtk.Align.FILL)
        self.volume_label.set_hexpand(True)
        self.volume_label.set_vexpand(False)

        self.volume.set_halign(Gtk.Align.FILL)
        self.volume.set_hexpand(True)
        self.volume.set_vexpand(False)

        self.volume_signal_id = self.volume.connect("value-changed", self.setAudio)
        self.volume.set_value(self.setPerc)
            
        audio_box.append(self.volume_label)
        audio_box.append(self.volume)

        audio_box.set_halign(Gtk.Align.FILL)
        audio_box.set_hexpand(True)
        audio_box.set_vexpand(False)

        control_center_grid.set_hexpand(True)
        control_center_grid.set_vexpand(False)

        # Setting Grid Objects
        control_center_grid.attach(self.wifi_button, 0, 0, 1, 1)
        control_center_grid.attach(self.bt_button, 0, 1, 1, 1)
        control_center_grid.attach(self.media_player.main, 1, 0, 1, 3)
        control_center_grid.attach(brightness_box, 0, 2, 2, 1)
        control_center_grid.attach(audio_box, 0, 3, 2, 1)

        self.control_center.set_child(control_center_grid)

        self.control_center.add_css_class("control-center")
        self.brightness.add_css_class("control-center-slide")
        self.wifi_button.add_css_class("wifi-button")
        self.bt_button.add_css_class("bt-button")

        self.wifi_counter = [1]
        self.bt_counter = [4]

        button.connect('clicked', self.on_control_center_click)
        self.wifi_button.connect('clicked', self.button_change, self.wifi_counter, "wifi-button")
        self.bt_button.connect('clicked', self.button_change, self.bt_counter, "bt-button")

        # Set Timers
        GLib.timeout_add_seconds(5, self.update_slider_from_system) # timer for brightness monitoring every 5s
        GLib.timeout_add_seconds(5, self.update_slider_audio) # timer for audio monitoring every 5s

    def button_change(self, button, counter, button_callback):
        
        if "wifi-button" == button_callback:
            if counter[0] == 1:
                counter[0] -= 1
                self.wifi_button.set_child(self.wifi_off)
                print(f"wifi off {counter}")
            elif counter[0] == 0:
                counter[0] += 1
                self.wifi_button.set_child(self.wifi_on)
                print(f"wifi on {counter}")

        elif "bt-button" == button_callback:
            if counter[0] == 4:
                counter[0] -= 1
                self.bt_button.set_child(self.bt_off)
                print(f"Bluetooth off {counter}")
            elif counter[0] == 3:
                counter[0] += 1
                self.bt_button.set_child(self.bt_on)
                print(f"bluetooth on {counter}")

    def displayBrightness(self):
        try:
            self.path = "/sys/class/backlight/intel_backlight/"

            with open(self.path + "max_brightness", "r") as bright:
                self.max_brightness = int(bright.read().strip())
            with open(self.path + "actual_brightness", "r") as bright:
                actual_brightness = int(bright.read().strip())
            self.perc = actual_brightness / self.max_brightness * 100
        except OSError as e:
            print(f"Something went wrong with reading brightness file: {e}")
        except PermissionError:
            print("File Permission Error")

    def setBrightness(self, scale):
        try:
            current_perc = scale.get_value()
            self.brightness_label.set_label(f"Brightness: {int(current_perc)}%")
            raw_target = int((current_perc / 100.0) * self.max_brightness)
            with open(self.path + "brightness", "w") as f:
                f.write(str(raw_target))
        except PermissionError:
            print("File Permission Error")

    def update_slider_from_system(self):
        try:
            with open(self.path + "actual_brightness", "r") as bright:
                current_actual = int(bright.read().strip())
            current_perc = (current_actual / self.max_brightness) * 100
            0
            # If structural hardware values changed outside our bar UI, sync layout
            if hasattr(self, 'brightness') and int(self.brightness.get_value()) != int(current_perc):
                # Block structural callback loops while updating tracking state
                self.brightness.handler_block(self.brightness_signal_id)
                
                self.brightness.set_value(current_perc)
                self.brightness_label.set_label(f"Brightness: {int(current_perc)}%")
                
                self.brightness.handler_unblock(self.brightness_signal_id)
        except Exception as e:
            print(f"Tracking error: {e}")
        return True

    def check_audio(self):
        try:
            audio_chk = Gio.Subprocess.new(["wpctl", "status"], Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_PIPE)
            audio_chk.communicate_utf8_async(None, None, self.audio_status)
        except GLib.GError as e:
            print(f"{e}")

    def audio_status(self, audio_chk, result):
        try:
            success, stdout, stderr = audio_chk.communicate_utf8_finish(result)

            if audio_chk.get_if_exited():
                if audio_chk.get_exit_status() == 0:
                    print("PipeWire is started")
                    currVolume = Gio.Subprocess.new(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"], Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_PIPE)
                    success, stdout, stderr = currVolume.communicate_utf8(None, None)
                    print(f"{stdout.split()[-1]}")
                    self.setPerc = float(stdout.split()[-1]) * 100
                    print(f"{self.setPerc}")
                else:
                    print("Still waiting on PipeWire")
                    GLib.timeout_add_seconds(1, self.audio_status)
        except GLib.GError as e:
            print(f"{e}")

    def setAudio(self, scale):
        try:
            aud_perc = scale.get_value()
            absVolume = aud_perc / 100
            setVolume = round(absVolume, 2)
            self.volume_label.set_label(f"Volume: {int(aud_perc)}%")
            subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{setVolume}"], capture_output=True, text=True)
        except OSError as e:
            print(f"Something went wrong with setting volume: {e}")

    def update_slider_audio(self):
        try:
            currVolume = subprocess.run(
                ["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"],
                capture_output=True,
                text=True
            )

            audio = currVolume.stdout.split()

            if not audio:
                return True

            current_perc = float(audio[1]) * 100

            # Don't update the slider if it is already correct
            if int(self.volume.get_value()) != int(current_perc):

                self.volume.handler_block(self.volume_signal_id)

                self.volume.set_value(current_perc)
                self.volume_label.set_label(
                    f"Volume: {int(current_perc)}%"
                )

                self.volume.handler_unblock(self.volume_signal_id)

        except Exception as e:
            print(f"Audio tracking error: {e}")

        return True

    def on_control_center_click(self, button):
        try:
            self.control_center.popup()
        except OSError as e:
            print(f"Something went wrong with your control center: {e}")