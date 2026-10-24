#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Eugene Nesterenko
"""Build an architecture-independent Debian package without root."""
from pathlib import Path
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
out = root / 'dist'
out.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='elegoo-package-') as temporary:
    stage = Path(temporary)
    def write(name, text, mode=0o644):
        path = stage / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        path.chmod(mode)
    write('DEBIAN/control', '''Package: elegoo-viewer
Version: 0.6.2
Section: video
Priority: optional
Architecture: all
Maintainer: Elegoo Viewer contributors <elegoo-viewer@localhost>
Depends: python3 (>= 3.8), python3-gi, iproute2, gir1.2-gtk-3.0, gir1.2-gdkpixbuf-2.0
Description: Standalone local camera viewer for Elegoo CC2
 A lightweight GTK application for viewing a local HTTP MJPEG camera stream.
 Saves the printer address and provides connect and disconnect controls.
''')
    write('usr/bin/elegoo-viewer', '#!/bin/sh\nexec /usr/bin/python3 /usr/share/elegoo-viewer/viewer.py "$@"\n', 0o755)
    for name in ('viewer.py', 'stream.py', 'discovery.py', 'profiles.py'):
        write('usr/share/elegoo-viewer/' + name, (root / name).read_text())
    write('usr/share/icons/hicolor/scalable/apps/elegoo-viewer.svg', (root / 'assets/elegoo-viewer.svg').read_text())
    for size in (16, 24, 32, 48, 64, 128, 256, 512):
        dest = stage / f'usr/share/icons/hicolor/{size}x{size}/apps/elegoo-viewer.png'
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / f'assets/elegoo-viewer-{size}.png', dest)
    write('usr/share/doc/elegoo-viewer/icon-attribution.md', (root / 'assets/README.md').read_text())
    photo = stage / 'usr/share/elegoo-viewer/assets/cc2-printer.jpg'
    photo.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root / 'assets/cc2-printer.jpg', photo)
    write('usr/share/applications/elegoo-viewer.desktop', (root / 'packaging/elegoo-viewer.desktop').read_text())
    write('usr/share/doc/elegoo-viewer/README.md', (root / 'README.md').read_text())
    doc_images = stage / 'usr/share/doc/elegoo-viewer/docs/images'
    shutil.copytree(root / 'docs/images', doc_images)
    write('usr/share/doc/elegoo-viewer/copyright', (root / 'COPYRIGHT').read_text())
    for name in ('LICENSE', 'THIRD_PARTY_NOTICES.md'):
        write('usr/share/doc/elegoo-viewer/' + name, (root / name).read_text())
    for source in (root / 'LICENSES').rglob('*'):
        if source.is_file():
            write('usr/share/doc/elegoo-viewer/LICENSES/' + str(source.relative_to(root / 'LICENSES')), source.read_text())
    subprocess.run(['dpkg-deb', '--root-owner-group', '--build', str(stage), str(out / 'elegoo-viewer_0.6.2_all.deb')], check=True)
