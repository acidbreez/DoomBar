import json
import os
import socket

import gi 

gi.require_version("Gtk", "4.0") # refer to gtk4
gi.require_version("Gdk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")

from gi.repository import Gtk, GLibUnix, GLib

class Events:
    def __init__(self, ws_box, HYPR_SOCK, HYPR_SOCK2):
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
        self.workspaces()
        # if the socket successfully connects then run active_workspaces to start GLib loop
        if self.sock:
            self.active_workspaces()

    def workspaces(self):
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

            for item in workspaces:
                ws = str(item["id"])
                
                self.ws_button = Gtk.Button()
                self.ws_label = Gtk.Label(label=ws)

                self.ws_button.set_child(self.ws_label)
                self.ws_box.append(self.ws_button)

                self.ws_name[ws] = self.ws_button

            return self.ws_box
        except OSError as e:
            print(f"Something went wrong with getting workspaces: {e}")

    def active_workspaces(self):
        GLibUnix.fd_add_full(
            GLib.PRIORITY_DEFAULT,
            self.sock.fileno(),
            GLib.IOCondition.IN,
            self.sock_callback,
            None
        )
                
    def sock_callback(self, fd, condition, user_data=None):
        try:
            if condition & GLib.IOCondition.IN:
                data = self.sock.recv(4096)
                
                if not data:
                    print("Socket got disconnected.")
                    return False

                real_data = data.decode('UTF-8')
                ws_data = real_data.splitlines()

                for ws_id in ws_data:
                    if "workspacev2>>" not in ws_id:
                        continue
                    
                    ws = ws_id.split(">>")
                    self.ws_id_final = ws[1].split(",").pop(1)

                for create_ws in ws_data:
                    if "createworkspacev2>>" not in create_ws:
                        continue

                    create_ws = create_ws.split(">>")
                    self.created_ws = create_ws[1].split(",").pop(1)

                    self.ws_button = Gtk.Button()
                    self.ws_label = Gtk.Label(label=self.created_ws)

                    self.ws_button.set_child(self.ws_label)
                    self.ws_box.append(self.ws_button)

                    self.ws_name[self.created_ws] = self.ws_button

                for del_ws in ws_data:
                    if "destroyworkspacev2>>" not in del_ws:
                        continue

                    del_ws = del_ws.split(">>")
                    self.destroy_ws = del_ws[1].split(",").pop(1).strip()

                    targeted_button = self.ws_name[self.destroy_ws]
                    self.ws_box.remove(targeted_button)
                    del self.ws_name[self.destroy_ws]
                    
            return True
        except OSError as e:
            print(f"Something went wrong with getting workspaces: {e}")
            return False