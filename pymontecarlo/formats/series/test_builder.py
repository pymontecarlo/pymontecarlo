#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.builder import SeriesBuilder

# Globals and constants variables.

class TestSeriesBuilder(TestCase):

    def setUp(self):
        super().setUp()

        self.builder = SeriesBuilder(self.settings)
        self.builder.add_column('a', 'b', 'foo')
        self.builder.add_column('c', 'd', 0.2, 'm', 0.01)
        self.builder.add_column('c', 'd', 6.0, 'm', error=True)

    def testbuild(self):
        s = self.builder.build(abbreviate_name=False, format_number=False)
        self.assertEqual('foo', s['a'])
        self.assertAlmostEqual(0.2, s['c [m]'], 4)
        self.assertAlmostEqual(6.0, s['\u03C3(c) [m]'], 4)

    def testbuild_abbreviate_name(self):
        s = self.builder.build(abbreviate_name=True, format_number=False)
        self.assertEqual('foo', s['b'])
        self.assertAlmostEqual(0.2, s['d[m]'], 4)
        self.assertAlmostEqual(6.0, s['\u03C3(d)[m]'], 4)

    def testbuild_format_number(self):
        s = self.builder.build(abbreviate_name=False, format_number=True)
        self.assertEqual('foo', s['a'])
        self.assertEqual('0.20', s['c [m]'])
        self.assertEqual('6', s['\u03C3(c) [m]'])

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
