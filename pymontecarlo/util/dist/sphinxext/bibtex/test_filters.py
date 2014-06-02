"""
================================================================================
:mod:`test_filters` -- Unit tests for the module :mod:`filters`.
================================================================================

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
import pymontecarlo.util.dist.sphinxext.bibtex.filters as filters

# Globals and constants variables.

class TestFilters(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testtitle_case(self):
        heading = "the vitamins are in my fresh california raisins"
        expected = "The Vitamins are in my Fresh California Raisins"
        self.assertEqual(expected, filters.title_case(heading))

        heading = "the vitamins are in my fresh {California raisins}"
        expected = "The Vitamins are in my Fresh California raisins"
        self.assertEqual(expected, filters.title_case(heading))

    def testsentence_case(self):
        heading = "the vitamins are in my fresh california raisins"
        expected = "The vitamins are in my fresh california raisins"
        self.assertEqual(expected, filters.sentence_case(heading))

        heading = "the vitamins are in my fresh {California} raisins"
        expected = "The vitamins are in my fresh California raisins"
        self.assertEqual(expected, filters.sentence_case(heading))

        heading = "the vitamins are in my fresh {California} raisins: vitamins and you"
        expected = "The vitamins are in my fresh California raisins: Vitamins and you"
        self.assertEqual(expected, filters.sentence_case(heading))

        heading = "the vitamins are in my fresh {California} raisins --- vitamins and you"
        expected = "The vitamins are in my fresh California raisins --- Vitamins and you"
        self.assertEqual(expected, filters.sentence_case(heading))

        heading = "the vitamins are in my fresh {California {Monte}} raisins"
        filters.sentence_case(heading)

    def testabbrev(self):
        text = "Charles Louis"
        expected = "C. L."
        self.assertEqual(expected, filters.abbrev(text))

        text = "Charles Louis"
        expected = "C.L."
        self.assertEqual(expected, filters.abbrev(text, sep=''))

        text = "C. Louis"
        expected = "C. L."
        self.assertEqual(expected, filters.abbrev(text))

        text = "Charles Louis-Xavier"
        expected = "C. L.-X."
        self.assertEqual(expected, filters.abbrev(text))

        text = "Charles Louis-Xavier Joseph de la Vall\'ee Poussin"
        expected = "C. L.-X. J. V. P."
        self.assertEqual(expected, filters.abbrev(text))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
