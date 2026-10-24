# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Eugene Nesterenko
"""Bounded, cancellable local IPv4 discovery using CC2 service ports."""
from concurrent.futures import ThreadPoolExecutor
import ipaddress
import json
import socket
import subprocess
from pathlib import Path


def local_targets():
    result = subprocess.run(['ip', '-j', '-4', 'addr', 'show', 'up'], capture_output=True, text=True, check=True, timeout=3)
    targets = set()
    for interface in json.loads(result.stdout):
        name = interface['ifname']
        if name == 'lo' or (Path('/sys/devices/virtual/net') / name).exists():
            continue
        for item in interface.get('addr_info', []):
            if item.get('scope') != 'global':
                continue
            address = ipaddress.IPv4Address(item['local'])
            # Limit large LANs to this computer's /24; never enumerate huge networks.
            prefix = max(24, item['prefixlen'])
            network = ipaddress.ip_network(f'{address}/{prefix}', strict=False)
            targets.update(str(host) for host in network.hosts() if host != address)
    if len(targets) > 1024:
        raise ValueError('Too many local addresses. Enter the printer IP manually.')
    return sorted(targets, key=ipaddress.IPv4Address)


def is_candidate(host, stopped):
    for port in (8080, 1883):
        if stopped.is_set():
            return False
        try:
            with socket.create_connection((host, port), timeout=0.35):
                pass
        except OSError:
            return False
    return True


def neighbor_macs():
    """Read same-link neighbor MACs; no root or external lookup required."""
    try:
        result = subprocess.run(['ip', '-j', '-4', 'neigh', 'show'], capture_output=True, text=True, check=True, timeout=3)
        entries = json.loads(result.stdout)
    except (OSError, ValueError, subprocess.SubprocessError):
        return {}
    import re
    return {item['dst']: item['lladdr'].lower() for item in entries
            if item.get('dst') and re.fullmatch(r'(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}', item.get('lladdr', ''))
            and not set(item.get('state', [])).intersection({'FAILED', 'INCOMPLETE'})}


def discover_devices(stopped, found, remembered_mac='', targets=None):
    """Return service candidates plus exact remembered MAC matches after probing."""
    remembered = {remembered_mac.lower()} if isinstance(remembered_mac, str) and remembered_mac else {m.lower() for m in remembered_mac} if remembered_mac else set()
    addresses = local_targets() if targets is None else targets
    candidates = []
    discover(stopped, candidates.append, addresses)
    if stopped.is_set():
        return
    neighbors = neighbor_macs()
    candidates = set(candidates)
    if remembered:
        candidates.update(host for host in addresses if neighbors.get(host) in remembered)
    for host in sorted(candidates, key=ipaddress.IPv4Address):
        if stopped.is_set():
            return
        mac = neighbors.get(host, '')
        found(host, mac, mac in remembered)


def discover(stopped, found, targets=None):
    addresses = local_targets() if targets is None else targets
    if not addresses:
        raise ValueError('No active local IPv4 network found. Enter the printer IP manually.')
    def probe(host):
        if is_candidate(host, stopped) and not stopped.is_set():
            found(host)
    with ThreadPoolExecutor(max_workers=32) as pool:
        list(pool.map(probe, addresses))
