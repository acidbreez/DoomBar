#!/usr/bin/python3

import ctypes

class gtk_layer_shell():
    def gtk_shell():
        try:
            ctypes.CDLL("libgtk4-layer-shell.so")
        except OSError as e:
           raise RuntimeError(
                "Could not load libgtk4-layer-shell.so. "
                "Install gtk4-layer-shell and its GObject introspection files."
            ) from e