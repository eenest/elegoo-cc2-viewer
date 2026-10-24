# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Eugene Nesterenko
import json
import tempfile
from pathlib import Path
import unittest
from profiles import load, save, upsert

class ProfileTests(unittest.TestCase):
    def test_migration(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'settings.json'
            path.write_text(json.dumps({'address':'192.168.1.2','mac':'88:49:2d:00:00:01'}))
            printers, selected=load(path)
            self.assertEqual(printers[0]['mac'],'88:49:2d:00:00:01')
            self.assertEqual(selected,printers[0]['id'])

    def test_add_edit_roundtrip_remove(self):
        printers, first=upsert([], 'Workshop', '192.168.1.2')
        printers, second=upsert(printers, 'Office', '192.168.1.3')
        printers, same=upsert(printers, 'Office renamed', '192.168.1.4', identity=second)
        self.assertEqual(same,second)
        self.assertEqual(len(printers),2)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'settings.json'
            save(path, printers, second)
            self.assertEqual(load(path),(printers,second))
            remaining=[p for p in printers if p['id']!=first]
            save(path,remaining,second)
            self.assertEqual(len(load(path)[0]),1)

    def test_reject_duplicate_and_invalid(self):
        printers,_=upsert([], 'Workshop', '192.168.1.2', '88:49:2d:00:00:01')
        for name, address, mac in [('Other','192.168.1.2',''),('Other','192.168.1.3','88:49:2d:00:00:01'),('','192.168.1.4',''),('Bad','not-an-ip','')]:
            with self.assertRaises(ValueError):
                upsert(printers,name,address,mac)
