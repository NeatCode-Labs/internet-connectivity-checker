#!/usr/bin/env python3
# Internet Connectivity Checker
# https://neatcodelabs.com/
# https://github.com/NeatCode-Labs

import gi
import os
import urllib.request
import time
import threading
import signal
import sys
import webbrowser

# Required GTK and AppIndicator imports
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, GLib, AppIndicator3, GdkPixbuf

# Configuration
CHECK_INTERVAL = 5  # seconds between connectivity checks
BLINK_INTERVAL = 0.5  # seconds between icon blinks when disconnected
TEST_URL = "https://www.google.com"  # URL to check for connectivity
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONNECTED_ICON = os.path.join(SCRIPT_DIR, "icons/gtk-connect.svg")
DISCONNECTED_ICON = os.path.join(SCRIPT_DIR, "icons/gtk-disconnect.svg")
MAX_ATTEMPTS = 3  # how many times to retry the HTTP check before declaring offline

class InternetConnectivityChecker:
    def __init__(self):
        self.indicator = AppIndicator3.Indicator.new(
            "internet-connectivity-checker",
            CONNECTED_ICON,
            AppIndicator3.IndicatorCategory.SYSTEM_SERVICES
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_title("Internet Connectivity Checker")
        
        # Create menu
        self.menu = Gtk.Menu()
        
        # Check Now menu item
        check_now_item = Gtk.MenuItem.new_with_label("Check Now")
        check_now_item.connect("activate", self.check_now)
        self.menu.append(check_now_item)
        
        # Separator
        self.menu.append(Gtk.SeparatorMenuItem())
        
        # Status menu item (read-only)
        self.status_item = Gtk.MenuItem.new_with_label("Status: Unknown")
        self.status_item.set_sensitive(False)
        self.menu.append(self.status_item)
        
        # Separator
        self.menu.append(Gtk.SeparatorMenuItem())
        
        # About menu item
        about_item = Gtk.MenuItem.new_with_label("About")
        about_item.connect("activate", self.show_about)
        self.menu.append(about_item)
        
        # Quit menu item
        quit_item = Gtk.MenuItem.new_with_label("Quit")
        quit_item.connect("activate", self.quit)
        self.menu.append(quit_item)
        
        self.menu.show_all()
        self.indicator.set_menu(self.menu)
        
        # State variables
        self.is_connected = False
        self.blink_state = False
        self.blink_thread = None
        self.blink_active = False
        
        # Start checking internet connectivity
        self.check_thread = threading.Thread(target=self.periodic_check, daemon=True)
        self.check_thread.start()
        
    def is_internet_connected(self):
        """Return True if any of the retry attempts succeeds."""
        for _ in range(MAX_ATTEMPTS):
            try:
                urllib.request.urlopen(TEST_URL, timeout=5)
                return True
            except:
                time.sleep(1)
        return False
    
    def check_now(self, _):
        self.check_connectivity()
    
    def check_connectivity(self):
        connected = self.is_internet_connected()
        GLib.idle_add(self.update_status, connected)
    
    def periodic_check(self):
        while True:
            self.check_connectivity()
            time.sleep(CHECK_INTERVAL)
    
    def update_status(self, connected):
        if connected != self.is_connected:
            self.is_connected = connected
            if connected:
                self.indicator.set_icon_full(CONNECTED_ICON, "Connected")
                self.status_item.set_label("Status: Connected")
                # Stop blinking if active
                self.blink_active = False
                if self.blink_thread and self.blink_thread.is_alive():
                    self.blink_thread.join(1.0)  # Give it time to finish
            else:
                self.indicator.set_icon_full(DISCONNECTED_ICON, "Disconnected")
                self.status_item.set_label("Status: Disconnected")
                # Start blinking
                self.start_blinking()
        return False
    
    def start_blinking(self):
        # Start blinking only if we're not already blinking
        if not self.blink_active:
            self.blink_active = True
            self.blink_thread = threading.Thread(target=self.blink_icon, daemon=True)
            self.blink_thread.start()
    
    def blink_icon(self):
        while self.blink_active and not self.is_connected:
            self.blink_state = not self.blink_state
            # Instead of toggling visibility, alternate between icons
            if self.blink_state:
                GLib.idle_add(self.indicator.set_icon_full, DISCONNECTED_ICON, "Disconnected")
            else:
                # Use the connected icon but with disconnected tooltip to maintain consistent size
                GLib.idle_add(self.indicator.set_icon_full, CONNECTED_ICON, "Disconnected")
            time.sleep(BLINK_INTERVAL)
        # Ensure the correct icon is shown when blinking stops
        if not self.is_connected:
            GLib.idle_add(self.indicator.set_icon_full, DISCONNECTED_ICON, "Disconnected")
    
    def show_about(self, _):
        # Create a custom dialog without AboutDialog quirks
        dialog = Gtk.Dialog(title="About Internet Connectivity Checker", 
                          modal=True,
                          destroy_with_parent=True)
        dialog.set_default_size(500, 350)
        dialog.set_border_width(15)
        content_area = dialog.get_content_area()
        content_area.set_spacing(10)
        content_area.set_vexpand(False)
        
        # Header with app icon
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        header_box.set_halign(Gtk.Align.CENTER)
        
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(CONNECTED_ICON)
            image = Gtk.Image.new_from_pixbuf(pixbuf)
        except:
            image = Gtk.Image.new_from_icon_name("network-workgroup", Gtk.IconSize.DIALOG)
        header_box.pack_start(image, False, False, 0)
        
        # App name
        name_label = Gtk.Label(label="Internet Connectivity Checker")
        name_label.set_markup("<span size='x-large' weight='bold'>Internet Connectivity Checker</span>")
        name_label.set_selectable(False)
        header_box.pack_start(name_label, False, False, 0)
        
        # Version
        version_label = Gtk.Label(label="1.0")
        version_label.set_selectable(False)
        header_box.pack_start(version_label, False, False, 0)
        
        # Description
        desc_label = Gtk.Label(label="A lightweight app that monitors internet connectivity")
        desc_label.set_selectable(False)
        desc_label.set_justify(Gtk.Justification.CENTER)
        header_box.pack_start(desc_label, False, False, 10)
        
        # Stats
        stats_text = (f"Checking connection to: {TEST_URL}\n"
                     f"Check interval: {CHECK_INTERVAL} seconds\n"
                     f"Blink interval: {BLINK_INTERVAL} seconds\n"
                     f"Retry attempts: {MAX_ATTEMPTS}")
        stats_label = Gtk.Label(label=stats_text)
        stats_label.set_selectable(False)
        stats_label.set_justify(Gtk.Justification.CENTER)
        header_box.pack_start(stats_label, False, False, 0)
        
        content_area.pack_start(header_box, False, False, 0)
        
        # Links
        link_markup = (
            '<span foreground="#81d4fa">'
            '<a href="https://neatcodelabs.com/">NeatCode Labs</a>'
            ' | '
            '<a href="https://github.com/NeatCode-Labs">Github</a>'
            '</span>'
        )
        link_label = Gtk.Label()
        link_label.set_markup(link_markup)
        link_label.set_halign(Gtk.Align.CENTER)
        link_label.set_selectable(False)
        link_label.set_margin_top(10)
        link_label.set_margin_bottom(15)
        content_area.pack_start(link_label, False, False, 0)
        
        # Define function to show Inspired by dialog
        def show_inspired_by(button):
            # Popover anchored to the Inspired by button
            popover = Gtk.Popover.new(button)
            popover.set_border_width(10)
            popover.set_modal(True)
            
            scrolled = Gtk.ScrolledWindow()
            scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            scrolled.set_min_content_width(450)
            scrolled.set_min_content_height(250)
            
            label = Gtk.Label()
            label.set_line_wrap(True)
            label.set_selectable(False)
            label.set_justify(Gtk.Justification.LEFT)
            label.set_markup(
                "Inspired by:\n\n" +
                "<a href='https://shropshirelug.wordpress.com/projects/ians-project-page/linux-system-tray-internet-status/'>" +
                "https://shropshirelug.wordpress.com/projects/ians-project-page/linux-system-tray-internet-status/" +
                "</a>\n\n" +
                "Author:      Ian Crane\n" +
                "Date:        24 Nov 2019\n" +
                "Original code from: " +
                "<a href='http://files.majorsilence.com/rubbish/pygtk-book/pygtk-notebook-html/pygtk-notebook-latest.html#SECTION00430000000000000000'>" +
                "http://files.majorsilence.com/rubbish/pygtk-book/pygtk-notebook-html/pygtk-notebook-latest.html#SECTION00430000000000000000" +
                "</a>"
            )
            scrolled.add(label)
            popover.add(scrolled)
            popover.show_all()
        
        # Create a bottom bar to hold the two buttons at opposite ends
        button_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_bar.set_halign(Gtk.Align.FILL)
        button_bar.set_valign(Gtk.Align.END)
        button_bar.set_hexpand(True)

        # Inspired by button (left)
        inspired_button = Gtk.Button(label="Inspired by")
        inspired_button.connect("clicked", show_inspired_by)
        button_bar.pack_start(inspired_button, False, False, 0)

        # Spacer expands in the middle to push buttons to corners
        spacer = Gtk.Box()
        button_bar.pack_start(spacer, True, True, 0)

        # Close button (right)
        close_button = Gtk.Button(label="Close")
        close_button.connect("clicked", lambda w: dialog.destroy())
        button_bar.pack_end(close_button, False, False, 0)

        content_area.pack_end(button_bar, False, False, 0)
        
        # Display the dialog
        dialog.show_all()
        dialog.run()
        dialog.destroy()
    
    def quit(self, _):
        Gtk.main_quit()

if __name__ == "__main__":
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, lambda sig, frame: Gtk.main_quit())
    
    # Start the app
    InternetConnectivityChecker()
    Gtk.main() 
