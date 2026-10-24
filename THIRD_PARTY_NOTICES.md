# Credits and third-party notices

## Project

Elegoo Viewer code and original materials: Copyright (C) 2026 Eugene Nesterenko, GPL-3.0-only. Full license in LICENSE. The GPL notice does not relicense third-party materials or trademarks.

## Included artwork

### ELEGOO logo — Simple Icons contributors

Source: https://github.com/simple-icons/simple-icons/blob/develop/icons/elegoo.svg
License: CC0-1.0; complete text in LICENSES/CC0-1.0.txt.
Files: assets/elegoo-logo.svg; logo path incorporated into assets/elegoo-viewer.svg and its PNG renderings. Modifications: white fill, scaling, blue rounded background, original camera badge. ELEGOO retains trademark rights; CC0 does not grant trademark rights. No endorsement is claimed.

### CC2 product photograph — ELEGOO

Source product page: https://www.elegoo.com/products/centauri-carbon-2-combo
Image: https://www.elegoo.com/cdn/shop/files/2.CC2C_14343a32-ac78-462b-b591-86ef465122ed.jpg?v=1772439271&width=600
File: assets/cc2-printer.jpg. Downloaded at 600 pixels; displayed scaled without editing the image.
Copyright belongs to ELEGOO / its rights holders; no open redistribution license or specific permission was established. This photograph is NOT licensed under the project's GPL. Included at the project owner's express request to identify the supported CC2 printer. This app is built specifically for the Elegoo Centauri Carbon 2. It is not affiliated with, sponsored by, or endorsed by ELEGOO. Attribution and this disclaimer do not grant rights in the photo. Confirm appropriate rights before further redistribution of this artwork.

## System runtime dependencies (not bundled)

- Python / standard library — Python Software Foundation and Python contributors; PSF license and associated notices. https://www.python.org/ and https://docs.python.org/3/license.html
- PyGObject — PyGObject contributors; LGPL-2.1-or-later. https://pygobject.gnome.org/
- GTK 3 / GDK — GTK contributors; LGPL-2.1-or-later for the library, with additional notices in the distribution package. https://www.gtk.org/
- GLib / GObject — GLib contributors; LGPL-2.1-or-later for the library. https://gitlab.gnome.org/GNOME/glib
- GdkPixbuf and image loaders — GdkPixbuf contributors; LGPL-2.1-or-later for the library; loaders have their own dependencies and notices. https://gitlab.gnome.org/GNOME/gdk-pixbuf
- iproute2 (`ip` command) — iproute2 contributors; primarily GPL-2.0-or-later with file-specific exceptions. https://git.kernel.org/pub/scm/network/iproute2/iproute2.git/

These are installed separately by Mint's package manager and remain replaceable system libraries/tools. Distribution copyright-file snapshots from the development system are included in LICENSES/system-notices/ for detailed author and license information. They are not a claim that the recipient has identical dependency versions. Current authoritative notices are in /usr/share/doc/<package>/copyright on the recipient's computer. Transitive dependencies are supplied and licensed by the operating system.

## Development and research acknowledgments

- bjan/pycentauri protocol documentation informed the CC2 MJPEG endpoint and discovery limitations: https://github.com/bjan/pycentauri/blob/main/docs/PROTOCOL.md . Reference only; no pycentauri code is copied or bundled.
- Simple Icons SVG source and Pictogrammers icon source were fetched from the upstream URLs above. Source assets are included; SHA256SUMS lists the vendored files.
- Debian dpkg-deb builds installers; Git manages sources. These development tools are not bundled. GNU GPL and Apache license texts are included verbatim from their publishers.
- Development assisted by OpenAI Codex. Codex is not included as a runtime component.

## License scope and historical releases

Version 0.5.0 places the application code under GPL-3.0-only. Third-party artwork retains its separate terms; the ELEGOO photograph is not offered under GPL. Older release archives and repository history retain their original terms and are not retroactively relicensed.
