#!/usr/bin/python3
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Eugene Nesterenko
"""Standalone Elegoo camera desktop application."""
import os
from pathlib import Path
import threading
import gi
import profiles

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GdkPixbuf
from stream import stream_url, read_frames
from discovery import discover_devices, neighbor_macs

VERSION = '0.6.2'
COPYRIGHT = 'Copyright © 2026 Eugene Nesterenko. Licensed under GNU GPL version 3.'

CONFIG = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')) / 'elegoo-viewer' / 'settings.json'


class Viewer(Gtk.Window):
    def __init__(self):
        super().__init__(title='Elegoo Viewer')
        self.set_default_size(900, 620)
        self.set_icon_name('elegoo-viewer')
        self.generation = 0
        self.search_stop = threading.Event()
        self.searching = False
        self.closed = False
        self.remembered_mac = ''
        self.printers, self.selected = profiles.load(CONFIG)
        self.refreshing = False
        self.stopped = threading.Event()
        self.running = False
        self.latest = None
        self.pixbuf = None
        self.lock = threading.Lock()
        self.connect('destroy', self.close)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(12)
        self.add(box)
        intro = Gtk.Label(label='CC2 camera • Enter the printer IP shown in its network settings')
        intro.set_xalign(0)
        header = Gtk.Box(spacing=8)
        header.pack_start(intro, True, True, 0)
        self.about_button = Gtk.Button(label='About')
        self.about_button.connect('clicked', self.show_about)
        header.pack_end(self.about_button, False, False, 0)
        self.screenshot_button = Gtk.Button(label='Save screenshot')
        self.screenshot_button.set_sensitive(False)
        self.screenshot_button.connect('clicked', self.save_screenshot)
        header.pack_end(self.screenshot_button, False, False, 0)
        box.pack_start(header, False, False, 0)
        saved_row = Gtk.Box(spacing=8)
        self.saved = Gtk.ComboBoxText()
        self.saved.set_hexpand(True)
        self.saved.connect('changed', self.choose_saved)
        saved_row.pack_start(self.saved, True, True, 0)
        for label, callback in [('Add printer', self.add_profile), ('Edit', self.edit_profile), ('Remove', self.remove_profile)]:
            control = Gtk.Button(label=label)
            control.connect('clicked', callback)
            saved_row.pack_start(control, False, False, 0)
        box.pack_start(saved_row, False, False, 0)
        row = Gtk.Box(spacing=8)
        self.address = Gtk.Entry()
        self.address.set_placeholder_text('Printer IP address (e.g. 192.168.1.33)')
        self.address.set_hexpand(True)
        self.address.connect('activate', self.toggle)
        row.pack_start(self.address, True, True, 0)
        self.find_button = Gtk.Button(label='Find printers')
        self.find_button.connect('clicked', self.find_printers)
        row.pack_start(self.find_button, False, False, 0)
        self.button = Gtk.Button(label='Connect')
        self.button.connect('clicked', self.toggle)
        row.pack_start(self.button, False, False, 0)
        box.pack_start(row, False, False, 0)
        self.results = Gtk.ComboBoxText()
        self.results.connect('changed', self.select_printer)
        box.pack_start(self.results, False, False, 0)
        self.image = Gtk.Image()
        self.placeholder = GdkPixbuf.Pixbuf.new_from_file(str(Path(__file__).resolve().parent / 'assets' / 'cc2-printer.jpg'))
        self.image.set_hexpand(True)
        self.image.set_vexpand(True)
        self.image.connect('size-allocate', self.resize)
        box.pack_start(self.image, True, True, 0)
        self.status = Gtk.Label(label='Ready. Connect on the same network as your printer.')
        self.status.set_line_wrap(True)
        self.status.set_xalign(0)
        box.pack_start(self.status, False, False, 0)
        self.timer = GLib.timeout_add(50, self.tick)
        self.refresh_saved()
        self.show_all()

    def show_about(self, *_):
        dialog = Gtk.AboutDialog(transient_for=self, modal=True)
        dialog.set_program_name('Elegoo Viewer')
        dialog.set_version(VERSION)
        dialog.set_copyright(COPYRIGHT)
        dialog.set_authors(['Eugene Nesterenko'])
        dialog.set_license_type(Gtk.License.GPL_3_0_ONLY)
        dialog.add_credit_section('Artwork', ['ELEGOO logo: Simple Icons contributors (CC0-1.0); trademark belongs to ELEGOO', 'CC2 product photograph: ELEGOO; used to identify the supported printer; not GPL-licensed'])
        dialog.add_credit_section('Runtime libraries', ['Python Software Foundation and Python contributors', 'PyGObject, GTK, GLib and GdkPixbuf contributors', 'iproute2 contributors'])
        dialog.add_credit_section('Protocol documentation', ['bjan/pycentauri (documentation reference; no code included)'])
        dialog.set_comments('Standalone local camera viewer for Elegoo Centauri Carbon 2.\nBuilt specifically for the Elegoo CC2. Product photo and logo belong to ELEGOO and identify the supported printer.\nNot affiliated with or endorsed by ELEGOO.\n\nPrinter requirements: stock firmware needs LAN-only mode. Alternatively, use compatible CC2 community firmware with local camera + cloud/web access enabled.')
        dialog.add_credit_section('Printer requirements', ['Stock firmware: enable LAN-only mode on the printer.', 'Alternatively, compatible CC2 community firmware must enable local camera alongside cloud/web access.'])
        dialog.set_logo_icon_name('elegoo-viewer')
        dialog.connect('response', lambda window, *_: window.destroy())
        dialog.show()

    def save_screenshot(self, *_):
        if self.pixbuf is None:
            return
        # Freeze the original-resolution frame while live video continues.
        frame = self.pixbuf.copy()
        from datetime import datetime
        dialog = Gtk.FileChooserDialog(title='Save camera screenshot', transient_for=self, action=Gtk.FileChooserAction.SAVE)
        dialog.add_buttons('Cancel', Gtk.ResponseType.CANCEL, 'Save', Gtk.ResponseType.OK)
        dialog.set_do_overwrite_confirmation(True)
        dialog.set_current_name('elegoo-' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.png')
        pictures = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES)
        if pictures and Path(pictures).is_dir():
            dialog.set_current_folder(pictures)
        image_filter = Gtk.FileFilter()
        image_filter.set_name('PNG image (*.png)')
        image_filter.add_pattern('*.png')
        dialog.add_filter(image_filter)
        while dialog.run() == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            if not filename:
                continue
            if not filename.lower().endswith('.png'):
                # Re-enter the dialog so replacement confirmation covers the actual PNG path.
                filename += '.png'
                dialog.set_filename(filename)
                dialog.set_current_name(Path(filename).name)
                continue
            try:
                frame.savev(filename, 'png', [], [])
            except (GLib.Error, OSError) as exc:
                error = Gtk.MessageDialog(transient_for=dialog, modal=True, message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.CLOSE, text='Could not save screenshot')
                error.format_secondary_text(str(exc))
                error.run()
                error.destroy()
                continue
            self.status.set_text('Screenshot saved: ' + filename)
            break
        dialog.destroy()

    def current_profile(self):
        return next((item for item in self.printers if item['id'] == self.selected), None)

    def refresh_saved(self):
        self.refreshing = True
        self.saved.remove_all()
        for item in self.printers:
            self.saved.append(item['id'], item['name'] + ' — ' + item['address'])
        self.saved.set_active_id(self.selected)
        self.refreshing = False
        item = self.current_profile()
        if item:
            self.address.set_text(item['address'])
            self.remembered_mac = item['mac']

    def persist_profiles(self):
        try:
            profiles.save(CONFIG, self.printers, self.selected)
            return True
        except OSError as exc:
            self.status.set_text('Could not save printers: ' + str(exc))
            return False

    def choose_saved(self, combo):
        if self.refreshing:
            return
        if self.running:
            self.disconnect()
        self.selected = combo.get_active_id() or ''
        self.refresh_saved()
        if self.persist_profiles():
            self.status.set_text('Printer selected. Click Connect to view its camera.')

    def profile_dialog(self, editing=False):
        item = self.current_profile() if editing else None
        if editing and not item:
            self.status.set_text('Select a saved printer to edit.')
            return
        dialog = Gtk.Dialog(title='Edit printer' if editing else 'Add printer', transient_for=self, modal=True)
        dialog.add_buttons('Cancel', Gtk.ResponseType.CANCEL, 'Save', Gtk.ResponseType.OK)
        content = dialog.get_content_area()
        content.set_spacing(8)
        content.set_border_width(12)
        name = Gtk.Entry()
        name.set_placeholder_text('Printer name, e.g. Workshop CC2')
        name.set_text(item['name'] if item else '')
        address = Gtk.Entry()
        address.set_placeholder_text('Printer IP address')
        address.set_text(item['address'] if item else self.address.get_text())
        content.pack_start(Gtk.Label(label='Name'), False, False, 0)
        content.pack_start(name, False, False, 0)
        content.pack_start(Gtk.Label(label='IP address'), False, False, 0)
        content.pack_start(address, False, False, 0)
        error = Gtk.Label()
        error.set_line_wrap(True)
        content.pack_start(error, False, False, 0)
        dialog.show_all()
        while dialog.run() == Gtk.ResponseType.OK:
            try:
                ip = address.get_text().strip()
                mac = neighbor_macs().get(ip, item['mac'] if item and ip == item['address'] else '')
                printers, selected = profiles.upsert(self.printers, name.get_text(), ip, mac, item['id'] if item else '')
                profiles.save(CONFIG, printers, selected)
            except (ValueError, OSError) as exc:
                error.set_text(str(exc))
                continue
            if self.running:
                self.disconnect()
            self.printers, self.selected = printers, selected
            self.refresh_saved()
            self.status.set_text('Printer saved. Click Connect to view its camera.')
            break
        dialog.destroy()

    def add_profile(self, *_):
        self.profile_dialog()

    def edit_profile(self, *_):
        self.profile_dialog(editing=True)

    def remove_profile(self, *_):
        item = self.current_profile()
        if not item:
            return
        remaining = [p for p in self.printers if p['id'] != item['id']]
        selected = remaining[0]['id'] if remaining else ''
        try:
            profiles.save(CONFIG, remaining, selected)
        except OSError as exc:
            self.status.set_text('Could not remove printer: ' + str(exc))
            return
        if self.running:
            self.disconnect()
        self.printers, self.selected = remaining, selected
        self.address.set_text('')
        self.remembered_mac = ''
        self.refresh_saved()
        self.status.set_text('Printer removed from this app.')

    def find_printers(self, *_):
        if self.searching:
            self.search_stop.set()
            self.find_button.set_sensitive(False)
            return
        self.searching = True
        self.search_stop = threading.Event()
        stopped = self.search_stop
        self.results.remove_all()
        self.results.set_sensitive(True)
        self.find_button.set_label('Stop search')
        self.status.set_text('Searching nearby addresses and remembered printer MAC…')
        self.found_count = 0
        def found(host, mac, remembered):
            GLib.idle_add(self.add_printer, stopped, host, mac, remembered)
        remembered_macs = [p['mac'] for p in self.printers if p['mac']]
        def run():
            message = ''
            try:
                discover_devices(stopped, found, remembered_macs)
            except Exception as exc:
                message = str(exc)
            GLib.idle_add(self.search_done, stopped, message)
        threading.Thread(target=run, daemon=True).start()

    def add_printer(self, stopped, host, mac, remembered):
        if not self.closed and stopped is self.search_stop and not stopped.is_set():
            profile = next((p for p in self.printers if mac and p['mac'] == mac), None)
            label = profile['name'] if profile else 'likely CC2'
            self.results.append(host, host + ' — ' + label + (' • ' + mac if mac else ''))
            self.found_count += 1
            if (self.found_count == 1 or remembered) and not self.running:
                self.results.set_active_id(host)
        return False

    def select_printer(self, combo):
        if not self.running and combo.get_active_id():
            host = combo.get_active_id()
            self.address.set_text(host)
            # Keep a discovered address separate until the user connects or saves it.

    def search_done(self, stopped, message):
        if self.closed or stopped is not self.search_stop:
            return False
        self.searching = False
        self.find_button.set_label('Find printers')
        self.find_button.set_sensitive(not self.running)
        if not self.running:
            if message:
                self.status.set_text(message)
            elif stopped.is_set():
                self.status.set_text('Search stopped. You can enter the printer IP manually.')
            elif self.found_count:
                self.status.set_text('Select a likely CC2 above, then Connect. Device identity is not verified.')
            else:
                self.status.set_text('No printers found nearby. Enter the printer IP manually; discovery may be blocked by network or printer settings.')
        return False

    def disconnect(self):
        self.stopped.set()
        self.generation += 1
        self.running = False
        self.address.set_sensitive(True)
        self.button.set_label('Connect')
        self.pixbuf = None
        self.screenshot_button.set_sensitive(False)
        self.resize()
        self.find_button.set_sensitive(True)
        self.results.set_sensitive(True)
        with self.lock:
            self.latest = None

    def toggle(self, *_):
        if self.running:
            self.disconnect()
            self.status.set_text('Disconnected.')
            return
        try:
            url = stream_url(self.address.get_text())
        except ValueError as exc:
            self.status.set_text(str(exc))
            return
        self.search_stop.set()
        self.find_button.set_sensitive(False)
        self.results.set_sensitive(False)
        warning = ''
        try:
            address = self.address.get_text().strip()
            item = next((p for p in self.printers if p['address'] == address), None)
            mac = neighbor_macs().get(address, item['mac'] if item else '')
            if not item and mac:
                item = next((p for p in self.printers if p['mac'] == mac), None)
            if item:
                item['address'] = address
                item['mac'] = mac
                self.selected = item['id']
            else:
                self.printers, self.selected = profiles.upsert(self.printers, 'CC2 ' + address, address, mac)
            self.remembered_mac = mac
            profiles.save(CONFIG, self.printers, self.selected)
            self.refresh_saved()
        except (OSError, ValueError):
            warning = ' (Could not save printer.)'
        self.generation += 1
        generation = self.generation
        stopped = threading.Event()
        self.stopped = stopped
        self.running = True
        self.pixbuf = None
        self.screenshot_button.set_sensitive(False)
        self.resize()
        self.address.set_sensitive(False)
        self.button.set_label('Disconnect')
        self.status.set_text('Connecting; waiting for video…' + warning)

        def frame(data):
            with self.lock:
                if generation == self.generation and not stopped.is_set():
                    self.latest = (generation, data)

        def receive():
            try:
                read_frames(url, stopped, frame)
            except Exception as exc:
                if not stopped.is_set():
                    GLib.idle_add(self.failed, generation, str(exc))
        threading.Thread(target=receive, daemon=True).start()

    def failed(self, generation, message):
        if generation == self.generation:
            self.disconnect()
            self.status.set_text('Video unavailable: ' + message + ' Check the IP. Stock firmware requires LAN-only mode; compatible community firmware must enable local camera + cloud/web access. Then reconnect.')
        return False

    def tick(self):
        with self.lock:
            pending, self.latest = self.latest, None
        if pending and pending[0] == self.generation:
            try:
                loader = GdkPixbuf.PixbufLoader.new_with_type('jpeg')
                loader.write(pending[1])
                loader.close()
                self.pixbuf = loader.get_pixbuf()
                self.screenshot_button.set_sensitive(True)
                self.resize()
                self.status.set_text('Live • Direct camera connection')
            except GLib.Error:
                self.status.set_text('Camera sent an invalid image; waiting for the next frame…')
        return True

    def resize(self, *_):
        picture = self.pixbuf if self.pixbuf else self.placeholder
        width = max(1, self.get_allocated_width() - 24)
        height = max(1, self.get_allocated_height() - 180)
        if self.pixbuf is None:
            width, height = min(width, 320), min(height, 320)
        scale = min(width / picture.get_width(), height / picture.get_height())
        self.image.set_from_pixbuf(picture.scale_simple(max(1, int(picture.get_width() * scale)), max(1, int(picture.get_height() * scale)), GdkPixbuf.InterpType.BILINEAR))

    def close(self, *_):
        self.closed = True
        self.search_stop.set()
        self.disconnect()
        GLib.source_remove(self.timer)
        Gtk.main_quit()


if __name__ == '__main__':
    Viewer()
    Gtk.main()
