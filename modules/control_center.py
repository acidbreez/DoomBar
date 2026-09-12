import os
import subprocess

from modules.media_player import MediaPlayer

from gi.repository import GdkPixbuf, Gio, Gtk, GLib
CONFIG = os.path.expanduser("~/.config/DoomBar/")

WIFION = (f"{CONFIG}theme/gentoo/gentoo_wifi.png")
WIFIOFF = (f"{CONFIG}theme/gentoo/gentoo_wifi_transparent.png")
BT_ON = (f"{CONFIG}theme/gentoo/gentoo_bt.png")
BT_OFF = (f"{CONFIG}theme/gentoo/gentoo_bt_transparent.png")
SPEAKER = (f"{CONFIG}theme/gentoo/gentoo_speaker.png")
MUTE = (f"{CONFIG}theme/gentoo/gentoo_mute.png")

class ControlCenter:
    def __init__(self, button):
        bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)

        self.wifi = True
        self.bluetooth = True
        self.muted = False

        self.setPerc = 0
        self.displayBrightness()
        self.check_audio()

        # Button Images
        pixbuf_off = GdkPixbuf.Pixbuf.new_from_file_at_scale( filename=WIFIOFF, width=40, height=40, preserve_aspect_ratio=True)
        self.wifi_off = Gtk.Image.new_from_pixbuf(pixbuf_off)
        self.wifi_off.set_hexpand(True)
        self.wifi_off.set_vexpand(False)
        self.wifi_off.set_pixel_size(40)
    
        pixbuf_on = GdkPixbuf.Pixbuf.new_from_file_at_scale( filename=WIFION, width=40, height=40, preserve_aspect_ratio=True )
        self.wifi_on = Gtk.Image.new_from_pixbuf(pixbuf_on)
        self.wifi_on.set_hexpand(True)
        self.wifi_on.set_vexpand(False)
        self.wifi_on.set_pixel_size(40)

        pixbuf_bt_off = GdkPixbuf.Pixbuf.new_from_file_at_scale( filename=BT_OFF, width=40, height=40, preserve_aspect_ratio=True)
        self.bt_off = Gtk.Image.new_from_pixbuf(pixbuf_bt_off)
        self.bt_off.set_hexpand(True)
        self.bt_off.set_vexpand(False)
        self.bt_off.set_pixel_size(40)

        pixbuf_bt_on = GdkPixbuf.Pixbuf.new_from_file_at_scale( filename=BT_ON, width=40, height=40, preserve_aspect_ratio=True)
        self.bt_on = Gtk.Image.new_from_pixbuf(pixbuf_bt_on)
        self.bt_on.set_hexpand(True)
        self.bt_on.set_vexpand(False)
        self.bt_on.set_pixel_size(40)

        pixbuf_speaker = GdkPixbuf.Pixbuf.new_from_file_at_scale( filename=SPEAKER, width= 40, height=40, preserve_aspect_ratio=True)
        self.speaker = Gtk.Image.new_from_pixbuf(pixbuf_speaker)
        self.speaker.set_hexpand(True)
        self.speaker.set_vexpand(False)
        self.speaker.set_pixel_size(40)

        pixbuf_mute = GdkPixbuf.Pixbuf.new_from_file_at_scale( filename=MUTE, width=40, height=40, preserve_aspect_ratio=True )
        self.mute = Gtk.Image.new_from_pixbuf(pixbuf_mute)
        self.mute.set_hexpand(True)
        self.mute.set_vexpand(False)
        self.mute.set_pixel_size(40)

        # Create Containers
        self.control_center = Gtk.Popover()
        control_center_grid = Gtk.Grid(column_spacing=0, row_spacing=0)
        brightness_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        audio_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Create Buttons
        self.wifi_button = Gtk.Button(child=self.wifi_on)
        self.bt_button = Gtk.Button(child=self.bt_on)
        self.speaker_button = Gtk.Button(child=self.speaker)

        # Create Widgets
        self.media_player = MediaPlayer(bus)

        # Create Labels
        self.brightness_label = Gtk.Label(label=f"Display Brightness: {int(self.perc)}%")
        self.volume_label = Gtk.Label(label=f"Volume: {int(self.setPerc)}%")

        # Create Sliders
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

        # Window Properties
        #self.control_center.set_size_request(300, 300)
        self.control_center.set_has_arrow(False)
        self.control_center.set_parent(button)

        control_center_grid.set_hexpand(True)
        control_center_grid.set_vexpand(True)
        control_center_grid.set_halign(Gtk.Align.FILL)
        control_center_grid.set_valign(Gtk.Align.FILL)

        self.wifi_button.set_hexpand(True)
        self.wifi_button.set_vexpand(True)
        self.wifi_button.set_halign(Gtk.Align.FILL)
        self.wifi_button.set_valign(Gtk.Align.FILL)

        self.bt_button.set_hexpand(True)
        self.bt_button.set_vexpand(True)
        self.bt_button.set_halign(Gtk.Align.FILL)
        self.bt_button.set_valign(Gtk.Align.FILL)

        self.media_player.main.set_hexpand(False)
        self.media_player.main.set_vexpand(True)
        self.media_player.main.set_halign(Gtk.Align.FILL)
        self.media_player.main.set_valign(Gtk.Align.FILL)

        brightness_box.set_hexpand(True)
        brightness_box.set_vexpand(False)
        brightness_box.set_halign(Gtk.Align.FILL)

        self.brightness_label.set_hexpand(True)
        self.brightness_label.set_vexpand(False)
        self.brightness_label.set_halign(Gtk.Align.FILL)
        self.brightness_label.set_valign(Gtk.Align.FILL)

        self.brightness.set_value(self.perc)
        self.brightness_signal_id = self.brightness.connect("value-changed", self.setBrightness)

        self.brightness.set_hexpand(True)
        self.brightness.set_vexpand(False)
        self.brightness.set_halign(Gtk.Align.FILL)

        brightness_box.append(self.brightness_label)
        brightness_box.append(self.brightness)

        audio_box.set_hexpand(True)
        audio_box.set_vexpand(False)
        audio_box.set_halign(Gtk.Align.FILL)

        audio_box.append(self.volume_label)
        audio_box.append(self.volume)

        self.volume_label.set_hexpand(True)
        self.volume_label.set_vexpand(False)
        self.volume_label.set_halign(Gtk.Align.FILL)
        self.volume_label.set_valign(Gtk.Align.FILL)

        self.volume_signal_id = self.volume.connect("value-changed", self.setAudio)
        self.volume.set_value(self.setPerc)

        self.volume.set_hexpand(True)
        self.volume.set_vexpand(False)
        self.volume.set_halign(Gtk.Align.FILL)

        # Grid layout
        control_center_grid.attach(self.media_player.main, 1, 0, 1, 3)
        control_center_grid.attach(self.wifi_button, 0, 0, 1, 1)
        control_center_grid.attach(self.bt_button, 0, 1, 1, 1)
        control_center_grid.attach(self.speaker_button, 0, 2, 1, 1)
        control_center_grid.attach(brightness_box, 0, 3, 2, 1)
        control_center_grid.attach(audio_box, 0, 4, 2, 1)

        # Layout
        self.control_center.set_child(control_center_grid)

        # CSS
        self.control_center.add_css_class("control-center")
        control_center_grid.add_css_class("control-center-grid")
        self.wifi_button.add_css_class("wifi-button")
        self.bt_button.add_css_class("bt-button")
        self.speaker_button.add_css_class("speaker-button")
        brightness_box.add_css_class("brightness-box")
        self.brightness.add_css_class("brightness-slider")
        audio_box.add_css_class("audio-box")
        self.volume.add_css_class("volume-slider")

        # Button Behaviours
        button.connect('clicked', self.on_control_center_click)
        self.wifi_button.connect('clicked', self.button_change, "wifi-button")
        self.bt_button.connect('clicked', self.button_change, "bt-button")
        self.speaker_button.connect('clicked', self.button_change, "speaker-button")

        self.update_slider_audio()
        # Set Timers
        GLib.timeout_add_seconds(5, self.update_slider_from_system) # timer for brightness monitoring every 5s
        GLib.timeout_add_seconds(5, self.update_slider_audio) # timer for audio monitoring every 5s

    def button_change(self, button, button_callback):
        if "wifi-button" == button_callback:
            # toggle some wifi option
            if self.wifi:
                self.wifi_button.set_child(self.wifi_off)
                self.wifi = False
                print(f"wifi off")
            else:
                self.wifi_button.set_child(self.wifi_on)
                self.wifi = True
                print(f"wifi on")

        elif "bt-button" == button_callback:
            # toggle some bluetooth option
            if self.bluetooth:
                self.bt_button.set_child(self.bt_off)
                self.bluetooth = False
                print(f"Bluetooth off")
            else:
                self.bt_button.set_child(self.bt_on)
                self.bluetooth = True
                print(f"bluetooth on")

        elif "speaker-button" == button_callback:
            mute = Gio.Subprocess.new(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"], Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_PIPE)
            if self.muted:
                self.speaker_button.set_child(self.speaker)
                self.muted = False
                print(f"Un-Muted")
            else:
                self.speaker_button.set_child(self.mute)
                self.muted = True
                print(f"Muted")

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
            self.brightness_label.set_label(f"Display Brightness: {int(current_perc)}%")
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
                self.brightness_label.set_label(f"Display Brightness: {int(current_perc)}%")
                
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
                    currVolume = Gio.Subprocess.new(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"], Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_PIPE)
                    success, stdout, stderr = currVolume.communicate_utf8(None, None)
                    self.setPerc = float(stdout.split()[-1]) * 100
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