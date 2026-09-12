import json
import os
import socket

import gi

gi.require_version("Gtk", "4.0") # refer to gtk4
gi.require_version("Gdk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")
gi.require_version("GLibUnix", "2.0")

from gi.repository import Gtk, GLibUnix, GLib

class Events:
    def __init__(self, ws_box, HYPR_SOCK, HYPR_SOCK2):
        super().__init__()

        # create container
        self.ws_box = ws_box
        self.HYPR_SOCK = HYPR_SOCK
        self.HYPR_SOCK2 = HYPR_SOCK2

        # Create workspace dictionary
        self.ws_name = {}

        # Connect to socket
        try:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.connect(self.HYPR_SOCK2)
            self.sock.setblocking(False)
        except OSError as e:
            print(f"Something went wrong trying to connect to the socket: {e}")
        except KeyboardInterrupt as e:
            self.sock.close()
            print("User quit.")

        # Setup buttons and put lables on from socket data
        self.get_workspaces()
        # if the socket successfully connects then run active_workspaces to start GLib loop
        if self.sock:
            self.check_ws()

    def check_vers(self):
        HYPR_CONFIG_LUA = os.path.expanduser("~/.config/hypr/hyprland.lua")
        HYPR_CONFIG_CONF = os.path.expanduser("~/.config/hypr/hyprland.conf")
        try:
            if os.path.exists(HYPR_CONFIG_LUA):
                self.WS_CHNG_CONF = f'eval hl.dispatch(hl.dsp.focus({{workspace = "{self.workspace_id}"}}))'
            elif os.path.exists(HYPR_CONFIG_CONF):
                self.WS_CHNG_CONF = f'dispatch workspace {self.workspace_id}'
            else:
                print(f"No Hypr Files Detected!")
        except OSError as e:
            print(f"Command not found: {e}")
        except FileExistsError as e:
            print(f"File path incorrect: {e}")

    def check_ws(self):
        GLibUnix.fd_add_full(
            GLib.PRIORITY_DEFAULT,
            self.sock.fileno(),
            GLib.IOCondition.IN,
            self.on_call,
            None
        )

    def get_workspaces(self):
        try:
            def cmd(command: str):
                try:
                    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                        sock.connect(self.HYPR_SOCK)
                        sock.sendall(command.encode("UTF-8"))
                        data = sock.recv(4096)
                    return json.loads(data.decode("UTF-8"))
                except OSError as e:
                    print(f"There is a problem with connecting to hyprland socket: {e}")
            
            workspaces = cmd("j/workspaces")
            self.create_button(workspaces)
            self.set_active_ws()
        except OSError as e:
            print(f"Something went wrong: {e}")
        
    def set_active_ws(self):
        try:
            def cmd(command: str):
                try:
                    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                        sock.connect(self.HYPR_SOCK)
                        sock.sendall(command.encode("UTF-8"))
                        data = sock.recv(4096)
                    return json.loads(data.decode("UTF-8"))
                except OSError as e:
                    print(f"There is a problem with connecting to hyprland socket: {e}")

            workspace = cmd("j/activeworkspace")
            
            for button in self.ws_name.values():
                button.remove_css_class("active")

            active_button = self.ws_name.get(str(workspace["id"]))

            if active_button:
                active_button.add_css_class("active")

        except OSError as e:
            print(f"Something went wrong: {e}")

    def create_button(self, data):
        try:
            for item in data:
                ws = str(item["id"])
                
                button = Gtk.Button(label=ws)
                button.add_css_class("workspace")

                self.ws_box.append(button)
                self.ws_name[ws] = button

                if ws == data:
                    button.add_css_class("active")

                button.connect('clicked', self.button_click)
            return self.ws_box
        except OSError as e:
            print(f"Something went wrong with getting workspaces: {e}")

    def button_click(self, button):
        try:
            self.workspace_id = button.get_label()
            self.check_vers()

            if button.get_label() is None:
                print(f"Invalid Button: {self.workspace_id}")
            else:
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                    sock.connect(self.HYPR_SOCK)
                    sock.sendall(self.WS_CHNG_CONF.encode("UTF-8"))
                self.set_active_ws()
                return

        except OSError as e:
            print(f"Something went wrong with: {e}")

    def on_call(self, fd, condition, user_data=None):
        try:
            if condition & GLib.IOCondition.IN:
                data = self.sock.recv(4096)
                
                if not data:
                    print("Socket got disconnected.")
                    return False

                real_data = data.decode('UTF-8')
                ws_data = real_data.splitlines()

                for create_ws in ws_data:
                    if "createworkspacev2>>" not in create_ws:
                        continue

                    create_ws = create_ws.split(">>")
                    self.created_ws = create_ws[1].split(",")[0].strip()

                    self.ws_button = Gtk.Button(label=self.created_ws)
                    self.ws_button.add_css_class("workspace")

                    self.ws_box.append(self.ws_button)
                    self.ws_name[self.created_ws] = self.ws_button

                    self.ws_button.connect("clicked", self.button_click)

                for del_ws in ws_data:
                    if "destroyworkspacev2>>" not in del_ws:
                        continue

                    del_ws = del_ws.split(">>")
                    self.destroy_ws = del_ws[1].split(",")[0].strip()

                    targeted_button = self.ws_name[self.destroy_ws]
                    self.ws_box.remove(targeted_button)
                    del self.ws_name[self.destroy_ws]

                for ws_id in ws_data:
                    if "workspacev2>>" not in ws_id:
                        continue
                    
                    ws = ws_id.split(">>")
                    self.ws_id_final = ws[1].split(",")[0].strip()
                    self.set_active_ws()

            return True
        except OSError as e:
            print(f"Something went wrong with getting workspaces: {e}")
            return False