# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Eugene Nesterenko
"""Persistent named printer profiles, including migration from the single printer app."""
import json
import uuid
from stream import stream_url


def load(path):
    try:
        data = json.loads(path.read_text())
        printers = data.get('printers')
        if not isinstance(printers, list):
            printers = [{'id': 'original', 'name': 'My CC2', 'address': data['address'], 'mac': data.get('mac', '')}] if data.get('address') else []
        valid = []
        ids = set()
        for item in printers:
            try:
                stream_url(item['address'])
                identity = item.get('id') or uuid.uuid4().hex
                if identity in ids:
                    continue
                valid.append({'id': identity, 'name': str(item.get('name') or 'CC2'), 'address': item['address'], 'mac': str(item.get('mac', ''))})
                ids.add(identity)
            except (ValueError, KeyError, TypeError, AttributeError):
                continue
        selected = data.get('selected', '')
        return valid, selected if selected in ids else (valid[0]['id'] if valid else '')
    except (OSError, ValueError, TypeError, AttributeError):
        return [], ''


def save(path, printers, selected):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps({'version': 2, 'printers': printers, 'selected': selected}, indent=2))
    temporary.replace(path)


def upsert(printers, name, address, mac='', identity=''):
    name, address = name.strip(), address.strip()
    if not name:
        raise ValueError('Enter a name for this printer.')
    stream_url(address)
    for item in printers:
        if item['id'] != identity and (item['address'] == address or (mac and item['mac'] == mac)):
            raise ValueError('This printer is already saved. Select it or edit its details.')
    entry = {'id': identity or uuid.uuid4().hex, 'name': name, 'address': address, 'mac': mac}
    return [entry if item['id'] == identity else dict(item) for item in printers] if identity else [*printers, entry], entry['id']
