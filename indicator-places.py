#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Very simple app-indicator, shows gtk-bookmarks (aka places)
# Author: Alex Simenduev <shamil.si@gmail.com>
# Modificado para elementaryOS por: http://entornosgnulinux.com/
#

import os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, Gio, AppIndicator3
import signal
import subprocess
import urllib.request, urllib.parse, urllib.error

APP_NAME = 'indicator-places'
APP_VERSION = '0.5'

class IndicatorPlaces:
    BOOKMARKS_PATH = os.getenv('HOME') + '/.config/gtk-3.0/bookmarks'

    def __init__(self):
        self.ind = AppIndicator3.Indicator.new("places", "system-file-manager", AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
        self.ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        self.update_menu()

    def create_menu_item(self, label, icon_name):
        image = Gtk.Image()
        image.set_from_icon_name(icon_name, 24)

        item = Gtk.ImageMenuItem()
        item.set_label(label)
        item.set_image(image)
        item.set_always_show_image(True)
        return item

    # This method gets a themed icon name
    def get_bookmark_icon(self, path):
        if path.startswith("smb") or path.startswith("ssh") or path.startswith("ftp") or path.startswith("network"):
            icon_name = "folder-remote"
        else:
            f = Gio.File.new_for_path(path)
            try:
                info = f.query_info(Gio.FILE_ATTRIBUTE_STANDARD_ICON)
                icon = info.get_icon()
                icon_name = icon.get_names()[0] if icon.get_names()[0] != '(null)' else 'folder'
            except:
                icon_name = "folder"

        return icon_name

    # This methind creates a menu
    def update_menu(self, widget = None, data = None):
        try:
            bookmarks = open(self.BOOKMARKS_PATH).readlines()
        except IOError:
            bookmarks = []

        # Create menu
        menu = Gtk.Menu()
        self.ind.set_menu(menu)

        # Home folder menu item
        item = self.create_menu_item("Home Folder", "user-home")
        item.connect("activate", self.on_bookmark_click, os.getenv('HOME'))
        menu.append(item)

        # Computer menu item
        item = self.create_menu_item("Computer", "computer" )
        item.connect("activate", self.on_bookmark_click, '/')
        menu.append(item)

        # Computer menu item
        item = self.create_menu_item("Network", "network-workgroup")
        item.connect("activate", self.on_bookmark_click, 'network://')
        menu.append(item)

        # Trash
        item = self.create_menu_item("Trash", "user-trash")
        item.connect("activate", self.on_bookmark_click, 'trash:///')
        menu.append(item)

        # Show separator
        item = Gtk.SeparatorMenuItem()
        menu.append(item)

        # Populate bookmarks menu items
        for bm in bookmarks:
            path, label = bm.strip().partition(' ')[::2]

            if not label:
                label = os.path.basename(os.path.normpath(path))

            label = urllib.parse.unquote(label)
            item = self.create_menu_item(label, self.get_bookmark_icon(path))
            item.connect("activate", self.on_bookmark_click, path)

            # Append the item to menu
            menu.append(item)

        # Show separator
        item = Gtk.SeparatorMenuItem()
        menu.append(item)

        # Quit menu item
        item = self.create_menu_item("Quit", "gtk-quit")
        item.connect("activate", Gtk.main_quit)
        menu.append(item)

        # Show the menu
        menu.show_all()

    # Open clicked bookmark
    def on_bookmark_click(self, widget, path):
        #subprocess.Popen('/usr/bin/nautilus %s' % path, shell = True)
        subprocess.Popen('/usr/bin/xdg-open %s' % path, shell = True)


    def on_bookmarks_changed(self, filemonitor, file, other_file, event_type):
        if event_type == Gio.FILE_MONITOR_EVENT_CHANGES_DONE_HINT:
            print('Bookmarks changed, updating menu...')
            self.update_menu()

if __name__ == "__main__":
    # Catch CTRL-C
    signal.signal(signal.SIGINT, lambda signal, frame: Gtk.main_quit())

    # Run the indicator
    i = IndicatorPlaces()

    # Monitor bookmarks changes
    file = Gio.File.new_for_path(i.BOOKMARKS_PATH)
    monitor = file.monitor_file(0, None)
    monitor.connect("changed", i.on_bookmarks_changed)

    # Main gtk loop
    Gtk.main()
