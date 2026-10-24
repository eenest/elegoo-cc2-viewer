# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Eugene Nesterenko
import threading
import unittest
from unittest.mock import patch, MagicMock
from discovery import local_targets, is_candidate, discover

class DiscoveryTests(unittest.TestCase):
    def test_large_subnet_is_bounded_and_self_excluded(self):
        response = MagicMock(stdout='[{"ifname":"testlan","addr_info":[{"scope":"global","local":"192.168.5.10","prefixlen":16}]}]')
        with patch('discovery.subprocess.run', return_value=response):
            targets = local_targets()
        self.assertEqual(len(targets), 253)
        self.assertNotIn('192.168.5.10', targets)
        self.assertTrue(all(host.startswith('192.168.5.') for host in targets))

    def test_both_ports_required(self):
        with patch('discovery.socket.create_connection', side_effect=[MagicMock(), OSError()]):
            self.assertFalse(is_candidate('192.168.1.2', threading.Event()))

    def test_cancel_skips_connections(self):
        stop = threading.Event(); stop.set()
        with patch('discovery.socket.create_connection') as connect:
            self.assertFalse(is_candidate('192.168.1.2', stop))
            connect.assert_not_called()

    def test_results_only_for_candidates(self):
        found = []
        with patch('discovery.is_candidate', side_effect=lambda host, _: host.endswith('.2')):
            discover(threading.Event(), found.append, ['192.168.1.1','192.168.1.2'])
        self.assertEqual(found, ['192.168.1.2'])

class MacDiscoveryTests(unittest.TestCase):
    def test_neighbor_filter_and_normalization(self):
        from discovery import neighbor_macs
        response = MagicMock(stdout='[{"dst":"192.168.1.2","lladdr":"88:49:2D:3D:8A:18","state":["STALE"]},{"dst":"192.168.1.3","state":["FAILED"]}]')
        with patch('discovery.subprocess.run', return_value=response):
            self.assertEqual(neighbor_macs(), {'192.168.1.2':'88:49:2d:3d:8a:18'})

    def test_remembered_mac_finds_new_ip_without_open_ports(self):
        from discovery import discover_devices
        found=[]
        with patch('discovery.discover'), patch('discovery.neighbor_macs', return_value={'192.168.1.7':'88:49:2d:3d:8a:18'}):
            discover_devices(threading.Event(), lambda *args: found.append(args), '88:49:2d:3d:8a:18', ['192.168.1.7'])
        self.assertEqual(found,[('192.168.1.7','88:49:2d:3d:8a:18',True)])

    def test_other_mac_and_other_network_not_matched(self):
        from discovery import discover_devices
        found=[]
        with patch('discovery.discover'), patch('discovery.neighbor_macs', return_value={'192.168.1.7':'88:49:2d:00:00:01','10.0.0.2':'88:49:2d:3d:8a:18'}):
            discover_devices(threading.Event(), lambda *args: found.append(args), '88:49:2d:3d:8a:18', ['192.168.1.7'])
        self.assertEqual(found,[])
