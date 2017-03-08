#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.util.datarow import DataRow
import pymontecarlo.util.units as units

# Globals and constants variables.

class TestDataRow(TestCase):

    def setUp(self):
        super().setUp()

        self.dr = DataRow()
        self.dr.add('a', 5.0, 0.0, 'm')
        self.dr.add('b', 4.0, 0.0, 'eV')
        self.dr.add('c', 1.0, 0.1, 'cm', 0.01)
        self.dr.add('d', 5.6, 0.5, unit='count/s')

    def test__len__(self):
        self.assertEqual(4, len(self.dr))

    def test__iter__(self):
        self.assertEqual(4, len(list(iter(self.dr))))

    def test__getitem__(self):
        q = self.dr['d']
        self.assertAlmostEqual(5.6, q.n, 4)
        self.assertAlmostEqual(0.5, q.s, 4)
        self.assertEqual(units.ureg.parse_units('counts/s'), q.units)

    def test__or__(self):
        dr2 = DataRow()
        dr2.add('a', 6.0, 0.0, 'm')
        dr2.add('f', 8.9, 0.4, 'A')

        dr3 = self.dr | dr2
        self.assertEqual(5, len(dr3))

        q = dr3['a']
        self.assertAlmostEqual(6.0, q.n, 4)
        self.assertAlmostEqual(0.0, q.s, 4)
        self.assertEqual(units.ureg.parse_units('m'), q.units)

    def test__ior__(self):
        dr2 = DataRow()
        dr2.add('a', 6.0, 0.0, 'm')
        dr2.add('f', 8.9, 0.4, 'A')

        self.dr |= dr2
        self.assertEqual(5, len(self.dr))

        q = self.dr['a']
        self.assertAlmostEqual(6.0, q.n, 4)
        self.assertAlmostEqual(0.0, q.s, 4)
        self.assertEqual(units.ureg.parse_units('m'), q.units)

    def test__xor__(self):
        dr2 = DataRow()
        dr2.add('a', 6.0, 0.0, 'm')
        dr2.add('b', 4.0, 0.0, 'eV')
        dr2.add('c', 1.0, 0.1, 'cm', 0.01)
        dr2.add('d', 5.6, 0.5, unit='count/s')
        dr2.add('f', 8.9, 0.4, 'A')

        dr3 = self.dr ^ dr2
        self.assertEqual(2, len(dr3))

        q = dr3['a']
        self.assertAlmostEqual(5.0, q.n, 4)
        self.assertAlmostEqual(0.0, q.s, 4)
        self.assertEqual(units.ureg.parse_units('m'), q.units)

    def test__xor__reversed(self):
        dr2 = DataRow()
        dr2.add('a', 6.0, 0.0, 'm')
        dr2.add('b', 4.0, 0.0, 'eV')
        dr2.add('c', 1.0, 0.1, 'cm', 0.01)
        dr2.add('d', 5.6, 0.5, unit='count/s')
        dr2.add('f', 8.9, 0.4, 'A')

        dr3 = dr2 ^ self.dr
        self.assertEqual(2, len(dr3))

        q = dr3['a']
        self.assertAlmostEqual(6.0, q.n, 4)
        self.assertAlmostEqual(0.0, q.s, 4)
        self.assertEqual(units.ureg.parse_units('m'), q.units)

    def test__xor__tolerance(self):
        # Difference above tolerance
        dr2 = DataRow()
        dr2.add('a', 5.0, 0.0, 'm')
        dr2.add('b', 4.0, 0.0, 'eV')
        dr2.add('c', 1.02, 0.1, 'cm', 0.01)
        dr2.add('d', 5.6, 0.5, unit='count/s')

        dr3 = dr2 ^ self.dr
        self.assertEqual(1, len(dr3))

        # Difference below tolerance
        dr2 = DataRow()
        dr2.add('a', 5.0, 0.0, 'm')
        dr2.add('b', 4.0, 0.0, 'eV')
        dr2.add('c', 1.001, 0.1, 'cm', 0.01)
        dr2.add('d', 5.6, 0.5, unit='count/s')

        dr3 = dr2 ^ self.dr
        self.assertEqual(0, len(dr3))

    def testupdate(self):
        dr2 = DataRow()
        dr2.add('a', 6.0, 0.0, 'm')
        dr2.add('f', 8.9, 0.4, 'A')

        self.dr.update(dr2)
        self.assertEqual(5, len(self.dr))

        q = self.dr['a']
        self.assertAlmostEqual(6.0, q.n, 4)
        self.assertAlmostEqual(0.0, q.s, 4)
        self.assertEqual(units.ureg.parse_units('m'), q.units)

    def testupdate_with_prefix(self):
        dr2 = DataRow()
        dr2.add('a', 6.0, 0.0, 'm')
        dr2.add('f', 8.9, 0.4, 'A')

        self.dr.update_with_prefix('foo-', dr2)
        self.assertEqual(6, len(self.dr))

        q = self.dr['a']
        self.assertAlmostEqual(5.0, q.n, 4)
        self.assertAlmostEqual(0.0, q.s, 4)
        self.assertEqual(units.ureg.parse_units('m'), q.units)

        q = self.dr['foo-a']
        self.assertAlmostEqual(6.0, q.n, 4)
        self.assertAlmostEqual(0.0, q.s, 4)
        self.assertEqual(units.ureg.parse_units('m'), q.units)

    def testcolumns(self):
        columns = self.dr.columns
        self.assertEqual(4, len(columns))
        self.assertEqual('a', columns[0])
        self.assertEqual('b', columns[1])
        self.assertEqual('c', columns[2])
        self.assertEqual('d', columns[3])

    def testtolist(self):
        out = self.dr.to_list()
        self.assertEqual(6, len(out))

        out = self.dr.to_list(['a', 'e'])
        self.assertEqual(2, len(out))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

