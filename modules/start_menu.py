import json
import inspect
import os
from pathlib import Path

import gi # import gtk module

gi.require_version("Gtk", "4.0") # refer to gtk4
gi.require_version("Gdk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")

from gi.repository import (
    Gdk,
    GdkPixbuf,
    Gio,
    GLib,
    Gtk,
    Gtk4LayerShell,
)

class StartMenu():
    def __init__(self):
        super().__init__()

        BASE_DIR = Path(__file__).resolve().parent.parent
        self.config_favs = (f"{BASE_DIR}/configs/favourites.json")

        # Pop up windows
        self.popover = Gtk.Popover() # start-menu css class

        # Pop up window settings
        self.popover.set_has_arrow(False)

        # Containers
        self.main_start_window = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=0)
        self.appList = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.favBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.searchAppBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        try:
            self.favourites = {}
            self.fav = {}

            if os.path.exists(self.config_favs) and os.path.getsize(self.config_favs) != 0:
                with open(self.config_favs, "r") as f:
                    self.fav = json.load(f)
                    print(f"{self.config_favs} opened successfully.")
            else:
                with open(self.config_favs, "w") as f:
                    self.fav = json.dump(self.favourites, f, indent=4)
                    print(f"File {self.config_favs} was created successfully.")
                f.close()
        except OSError as e:
            print(f"Something went wrong with {self.config_favs}: {e}")

        # Entry
        self.search_entry = Gtk.SearchEntry()

        # Search Bar
        self.search_entry.set_placeholder_text("Search applications...")
        self.search_entry.set_focusable(True)
        self.search_entry.set_text("")
        self.search_entry.connect("activate", self.searchRes)

        self.startMenu()
        self.add_favourite()
        
        self.appList.set_hexpand(True)
        self.appList.set_vexpand(True)
        self.search_entry.set_hexpand(True)
        self.search_entry.set_vexpand(False)

        # CSS settings
        self.popover.add_css_class("start-menu")
        self.main_start_window.add_css_class("main-start-window")

        self.appList.add_css_class("app-list")
        self.scrolled_box.add_css_class("scrolled-box")

        self.favBox.add_css_class("favourites")
        self.searchAppBox.add_css_class("search-box")
        self.sear_label_box.add_css_class("search-label")
        
    def appCategories(self):
        try:
            categorized_apps = {}
            
            all_apps = Gio.AppInfo.get_all()
            for app in all_apps:
                if not app.should_show():
                    continue

                categories_str = app.get_categories()
                
                if categories_str:
                    # Split string into a list and filter out empty items
                    cats = [c for c in categories_str.split(';') if c]
                    # Use the primary/first category assigned to the app
                    primary_cat = cats[0]
                else:
                    primary_cat = "Other"

                # Initialize the category list if it doesn't exist
                if primary_cat not in categorized_apps:
                    categorized_apps[primary_cat] = []

                # Append the Gio.AppInfo object to the category list
                categorized_apps[primary_cat].append(app)

            return categorized_apps

        except Exception as e:
            print(f"There was an error grabbing categories for start menu: {e}")
            return {}

    def startMenu(self):
        try:
            # Grid settings
            grid = Gtk.Grid(column_spacing=0, row_spacing=0)
            grid.set_column_homogeneous(False)
            grid.set_hexpand(True)
            grid.set_vexpand(True)
            
            # Scrolled Windows
            self.scrolled_box = Gtk.ScrolledWindow()

            self.scrolled_box.set_overlay_scrolling(False)
            favourites = Gtk.ScrolledWindow()
            search_results = Gtk.ScrolledWindow()

            # Scrolled Window Settings
            self.scrolled_box.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            self.scrolled_box.set_hexpand(True)
            self.scrolled_box.set_vexpand(True)

            favourites.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            favourites.set_size_request(275, 200)
            favourites.set_hexpand(True)
            favourites.set_vexpand(True)

            search_results.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            search_results.set_size_request(275, 200)
            search_results.set_hexpand(True)
            search_results.set_vexpand(True)

            # Get the organized applications dictionary
            organized_apps = self.appCategories()

            for category, apps in organized_apps.items():
                # Add a stylized category section label
                catButton = Gtk.Button(label=f"{category}")
                catButton.set_halign(Gtk.Align.FILL)

                catButton.set_focusable(False)
                catButton.set_focus_on_click(False)

                self.appList.append(catButton)

                for app in apps:
                    app_name = app.get_name()
                    app_icon = app.get_icon()
                    
                    button_layout = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
                    if app_icon:
                        img = Gtk.Image.new_from_gicon(app_icon)
                        img.set_icon_size(Gtk.IconSize.NORMAL)
                    else:
                        img = Gtk.Image.new_from_icon_name("application-x-executable")
                    
                    appLabel = Gtk.Label(label=app_name)
                    appLabel.set_halign(Gtk.Align.START)

                    button_layout.append(img)
                    button_layout.append(appLabel)

                    app_button = Gtk.Button(child=button_layout)

                    app_button.set_hexpand(True)
                    app_button.set_halign(Gtk.Align.FILL)

                    app_button.set_focusable(False)
                    app_button.set_focus_on_click(False)

                    button_layout.set_hexpand(True)
                    button_layout.set_halign(Gtk.Align.FILL)

                    app_button.connect('clicked', self.on_app_click, app)

                    self.appList.append(app_button)

                    # Right click gesture to add favorites settings
                    right_click_add = Gtk.GestureClick.new()
                    right_click_add.set_button(3)

                    right_click_add.connect("pressed", self.on_right_click, app)
                    app_button.add_controller(right_click_add)

            favLabel = Gtk.Label(label="Favourites")
            self.favBox.append(favLabel)

            self.sear_label_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.sear_label_box.set_hexpand(True)
            self.sear_label_box.set_vexpand(True)

            searLabel = Gtk.Label(label="Search")
            searLabel.set_halign(Gtk.Align.FILL)

            self.sear_label_box.append(searLabel)
            self.sear_label_box.append(search_results)

            self.scrolled_box.set_child(self.appList)
            favourites.set_child(self.favBox)
            search_results.set_child(self.searchAppBox)

            # Attach widgets to the grid (widget, column, row, width, height)
            grid.attach(self.scrolled_box, 0, 0, 1, 2)
            grid.attach(favourites, 1, 0, 2, 1)
            grid.attach(self.sear_label_box, 1, 1, 2, 1)
            grid.attach(self.search_entry, 0, 2, 3, 1)

            self.main_start_window.append(grid)
            self.popover.set_child(self.main_start_window)
        except Exception as e:
            print(f"There was an error with your start menu: {e}")

    def add_favourite(self):
        try:
            for item in self.fav:
                app = Gio.DesktopAppInfo.new(item)

                if app:
                    self.create_favourite_button(app, "add_favourite")
        except OSError as e:
            print(f"There was an issue: {e}")

    def create_favourite_button(self, app, callback_name):
        fav_icon = app.get_icon()
        name = app.get_name()

        layout = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

        if fav_icon:
            favImg = Gtk.Image.new_from_gicon(fav_icon)
            favImg.set_icon_size(Gtk.IconSize.NORMAL)
        else:
            favImg = Gtk.Image.new_from_icon_name(
                "application-x-executable"
            )

        fav_button_label = Gtk.Label(label=name)
        fav_button_label.set_halign(Gtk.Align.START)

        layout.append(favImg)
        layout.append(fav_button_label)

        button = Gtk.Button(child=layout)

        button.set_hexpand(True)
        button.set_halign(Gtk.Align.FILL)

        layout.set_hexpand(True)
        layout.set_halign(Gtk.Align.FILL)

        button.connect('clicked', self.on_app_click, app)
    
        if "add_favourite" == callback_name:
            self.favBox.append(button)

            # Right-click to delete favourite
            right_click_del = Gtk.GestureClick.new()
            right_click_del.set_button(3)
            right_click_del.connect("pressed", self.right_click_del, app)

            button.add_controller(right_click_del)

        elif "searchRes" == callback_name:
            self.searchAppBox.append(button)

    def right_click_del(self, gesture, n_press, x, y, app):
        app_name = app.get_id()

        with open(self.config_favs, "r") as file:
            self.favourites = json.load(file)

        if app_name in self.favourites:
            del self.favourites[app_name]

        with open(self.config_favs, "w") as file:
            json.dump(self.favourites, file, indent=4)

        # Remove the button from the GTK UI
        button = gesture.get_widget()
        self.favBox.remove(button)

    def searchRes(self, entry):

        input = self.search_entry.get_text().casefold()
        
        try:
            all_apps = Gio.AppInfo.get_all()

            while child := self.searchAppBox.get_first_child():
                self.searchAppBox.remove(child)

            for app in all_apps:
                appName = app.get_name().casefold()
                app_icon = app.get_icon()
                    
                if input in appName:
                    self.create_favourite_button(app, "searchRes")
                    self.search_entry.set_text("")
        except OSError as e:
            print(f"Something went wrong with your search: {e}")

    def on_app_click(self, button, app):
        try:
            context = Gio.AppLaunchContext()
            app.launch([], context)
            self.popover.popdown()
        except Exception as e:
            print(f"Failed to launch application: {e}")

    def pin_fav(self, app_name):
        try:
            if app_name in self.favourites:
                print(f"{app_name} is already a favourite")
                return

            self.favourites[app_name] = True

            with open(self.config_favs, "w") as file:
                json.dump(self.favourites, file, indent=4)
            app = Gio.DesktopAppInfo.new(app_name)
            if app:
                self.create_favourite_button(app, "add_favourite")
        except OSError as e:
            print(f"There was an issue pinning to your favourites: {e}")

    def on_right_click(self, gesture, n_press, x, y, app):
        try:
            app_name = app.get_id()

            with open(self.config_favs, "r") as self.file:
                self.favourites = json.load(self.file)
            self.pin_fav(app_name)
                
        except Exception as e:
            print(f"Failed to pin application to favourites: {e}")