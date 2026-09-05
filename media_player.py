import gi
import threading
import urllib.request

# abcdefghijklmnopqrstuvwxyz
from gi.repository import GdkPixbuf, Gdk, Gio, GLib, Gtk

ART_SIZE = 125

class MediaPlayer(Gtk.Box):
    def __init__(self):
        super().__init__()

        bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)

        self.media_proxy = Gio.DBusProxy.new_sync(
            bus,
            Gio.DBusProxyFlags.NONE,
            None,
            "org.mpris.MediaPlayer2.cider",
            "/org/mpris/MediaPlayer2",
            "org.mpris.MediaPlayer2.Player",
            None
        )

        self.media_proxy.connect(
            "g-properties-changed",
            self.dbus_update
        )

        self.art = Gtk.Picture()
        self.art.set_can_shrink(True)
        self.art.set_keep_aspect_ratio(True)
        self.art.set_content_fit(Gtk.ContentFit.CONTAIN)

        self.art.set_hexpand(False)
        self.art.set_vexpand(False)
        self.art.set_halign(Gtk.Align.CENTER)
        self.art.set_valign(Gtk.Align.CENTER)

        self.layout()

    def layout(self):
        grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        control_grid = Gtk.Grid(orientation=Gtk.Orientation.HORIZONTAL)
        metaData_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        box_art = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)        

        grid.set_hexpand(False)
        grid.set_vexpand(False)
        grid.set_halign(Gtk.Align.CENTER)
        grid.set_valign(Gtk.Align.CENTER)

        control_grid.set_hexpand(False)
        control_grid.set_halign(Gtk.Align.FILL)
        control_grid.set_column_homogeneous(True)
        control_grid.set_halign(Gtk.Align.CENTER)
        control_grid.set_valign(Gtk.Align.CENTER)

        ctrl_but_prev = Gtk.Button()
        ctrl_but_pause = Gtk.Button()
        ctrl_but_next = Gtk.Button()
        
        ctrl_but_prev.set_label(label="󰒮")
        ctrl_but_pause.set_label(label="󰏤")        
        ctrl_but_next.set_label(label="󰒭")

        play_counter = [0]

        ctrl_but_prev.connect('clicked', self.dbus_command, "Previous", "")
        ctrl_but_pause.connect('clicked', self.dbus_command, "PlayPause", play_counter)
        ctrl_but_next.connect('clicked', self.dbus_command, "Next", "")

        self.set_hexpand(False)
        self.set_vexpand(False)
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)

        metaData_box.set_hexpand(False)
        metaData_box.set_vexpand(False)
        metaData_box.set_halign(Gtk.Align.CENTER)
        metaData_box.set_valign(Gtk.Align.CENTER)

        box_art.set_hexpand(False)
        box_art.set_vexpand(False)

        control_box.set_hexpand(False)
        control_box.set_vexpand(False)
        control_box.set_halign(Gtk.Align.CENTER)
        
        box_art.append(self.art)
        metaData_box.append(box_art)

        control_grid.attach(ctrl_but_prev, 0, 0, 1, 1)
        control_grid.attach(ctrl_but_pause, 1, 0, 1, 1)
        control_grid.attach(ctrl_but_next, 2, 0, 1, 1)

        control_box.append(control_grid)

        grid.attach(metaData_box, 0, 0, 1, 1)
        grid.attach(control_box, 0, 1, 1, 1)

        self.append(grid)

        self.add_css_class("media-player")
        metaData_box.add_css_class("meta-data-box")
        control_box.add_css_class("controls")
        ctrl_but_prev.add_css_class("prev-button")
        ctrl_but_pause.add_css_class("pause-button")
        ctrl_but_next.add_css_class("next-button")

        self.get_art()

    def dbus_command(self, button, command, play_counter):
        self.media_proxy.call_sync(
            command, # MethodName
            None, # arguments
            Gio.DBusProxyFlags.NONE,
            -1, # default timer to wait
            None
        )

        if command == "PlayPause":
            if play_counter[0] == 1:
                button.set_label(label="󰐊")
                play_counter[0] -= 1
            elif play_counter[0] == 0:
                button.set_label(label="󰏤")
                play_counter[0] += 1

    def dbus_update(self, proxy, changed_properties, invalidated_properties):
        if "Metadata" in changed_properties.unpack():
            metadata = changed_properties["Metadata"]

            self.get_art()

    def get_art(self):
        media_art = self.media_proxy.get_cached_property("Metadata")

        if media_art is None:
            return
        media_art = media_art.unpack()
        media_url = media_art.get("mpris:artUrl")

        threading.Thread(target=self.download_art, args=(media_url,), daemon=True).start()

    def download_art(self, media_url):
        try:
            raw_data = urllib.request.urlopen(media_url).read()

            GLib.idle_add(self.update_ui_with_image, raw_data)
        except Exception as e:
            print(f"Failed to download image: {e}")

    def update_ui_with_image(self, raw_data):
        input_stream = Gio.MemoryInputStream.new_from_data(raw_data, None)
        pixbuf = GdkPixbuf.Pixbuf.new_from_stream_at_scale(input_stream, ART_SIZE, ART_SIZE, True, None)
        texture = Gdk.Texture.new_for_pixbuf(pixbuf)

        self.art.set_paintable(texture)

        return False
