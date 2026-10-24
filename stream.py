# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Eugene Nesterenko
"""HTTP MJPEG transport, independent of the desktop UI."""
import urllib.parse
import urllib.request


def stream_url(address):
    import ipaddress
    try:
        host = ipaddress.ip_address(address.strip())
    except ValueError as exc:
        raise ValueError('Enter the printer IP address, for example 192.168.1.33.') from exc
    value = '[' + str(host) + ']' if host.version == 6 else str(host)
    return f'http://{value}:8080/?action=stream'


def read_frames(url, stopped, on_frame):
    request = urllib.request.Request(url, headers={'User-Agent': 'ElegooViewer/0.6.2'})
    # Local printer access must not be routed through a system HTTP proxy.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(request, timeout=5) as response:
        buf = b''
        while not stopped.is_set():
            chunk = response.read1(32768)
            if not chunk:
                raise OSError('Camera closed the connection.')
            buf += chunk
            while not stopped.is_set():
                start = buf.find(b'\xff\xd8')
                if start < 0:
                    buf = buf[-1:]
                    break
                buf = buf[start:]
                end = buf.find(b'\xff\xd9', 2)
                if end < 0:
                    break
                on_frame(buf[:end + 2])
                buf = buf[end + 2:]
            if len(buf) > 8_000_000:
                raise OSError('Camera frame exceeds 8 MB.')
