# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Eugene Nesterenko
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from stream import stream_url, read_frames


class TransportTests(unittest.TestCase):
    def test_addresses(self):
        self.assertEqual(stream_url('192.168.1.80'), 'http://192.168.1.80:8080/?action=stream')
        self.assertEqual(stream_url('::1'), 'http://[::1]:8080/?action=stream')
        for address in ('', 'file:///tmp/image', 'http://host:bad', 'http://user:pass@host'):
            with self.assertRaises(ValueError):
                stream_url(address)

    def test_fragmented_stream_and_cancellation(self):
        frames = [b'\xff\xd8one\xff\xd9', b'\xff\xd8two\xff\xd9']
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
                self.end_headers()
                for byte in b'headers\r\n' + b'\r\n--frame\r\n'.join(frames):
                    self.wfile.write(bytes([byte]))
                    self.wfile.flush()
            def log_message(self, *_):
                pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        stopped = threading.Event()
        received = []
        def accept(frame):
            received.append(frame)
            if len(received) == 2:
                stopped.set()
        try:
            read_frames(f'http://127.0.0.1:{server.server_port}/', stopped, accept)
            self.assertEqual(received, frames)
        finally:
            server.shutdown()
            server.server_close()

    def test_connection_failure(self):
        from unittest.mock import patch
        with patch('urllib.request.OpenerDirector.open', side_effect=OSError('unavailable')):
            with self.assertRaises(OSError):
                read_frames('http://localhost/', threading.Event(), lambda _: None)
