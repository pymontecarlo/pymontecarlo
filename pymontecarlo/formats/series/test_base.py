#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.base import NamedSeriesColumn, ErrorSeriesColumn

# Globals and constants variables.

class TestNamedSeriesColumn(TestCase):

    def setUp(self):
        super().setUp()

        self.column0 = NamedSeriesColumn('a', 'b')
        self.column1 = NamedSeriesColumn('a', 'b', 'm', 0.1)

    def testcompare(self):
        self.assertTrue(self.column0.compare('foo', 'foo'))
        self.assertFalse(self.column0.compare('foo', 'bar'))

        self.assertTrue(self.column1.compare(0.0, 0.05))
        self.assertFalse(self.column1.compare(0.0, 0.2))

    def testformat_value(self):
        self.assertEqual('foo', self.column0.format_value('foo'))
        self.assertEqual('{:g}'.format(1.0), self.column0.format_value(1.0))

        self.assertEqual('{:.1f}'.format(2.0), self.column1.format_value(2.0))
        self.assertEqual('{:.1f}'.format(0.2), self.column1.format_value(0.2))

class TestErrorSeriesColumn(TestCase):

    def setUp(self):
        super().setUp()

        parent = NamedSeriesColumn('a', 'b', 'm', 0.1)
        self.column = ErrorSeriesColumn(parent)

    def testskeleton(self):
        self.assertEqual('\u03C3(a)', self.column.name)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
