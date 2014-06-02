"""
================================================================================
:mod:`test_style` -- Unit tests for the module :mod:`style`.
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
import os
import re

# Third party modules.
from pybtex.database.input.bibtex import Parser as BibtexParser

# Local modules.
from pymontecarlo.util.dist.sphinxext.bibtex.style import Style
from pymontecarlo.util.dist.sphinxext.bibtex.convert import \
    pybtex_entry_to_dict as to_dict

# Globals and constants variables.

class TestStyle(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        curdir = os.path.dirname(os.path.abspath(__file__))

        parser = BibtexParser()
        self.entries = \
            parser.parse_file(os.path.join(curdir, 'testdata', 'bibtex.bib')).entries

        self.style = Style(os.path.join(curdir, 'styles'), 'apa')

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def _remove_whitespaces(self, text):
        text = re.sub("\s+", " ", text)
        text = re.sub("&nbsp;", " ", text)
        text = re.sub("&amp;", "&", text)
        return text.strip()

    def testbook(self):
        # Basic Format for Books
        entry = self.entries['Calfee1991']
        expected = "Calfee, R. C., & Valencia, R. R. (1991). APA guide to preparing manuscripts for journal publication. Washington, DC: American Psychological Association."
        actual = self._remove_whitespaces(self.style.render(to_dict(entry)))
        self.assertEqual(expected, actual)

        # Edited Book, No Author
        entry = self.entries['Duncan1997']
        expected = "Duncan, G. J., & Brooks-Gunn, J. (Eds.). (1997). Consequences of growing up poor. New York, NY: Russell Sage Foundation."
        actual = self._remove_whitespaces(self.style.render(to_dict(entry)))
        self.assertEqual(expected, actual)

        # Edited Book with an Author or Authors
        entry = self.entries['Plath2000']
        expected = "Plath, S. (2000). The unabridged journals. Kukil, K. V. (Ed.). New York, NY: Anchor."
        actual = self._remove_whitespaces(self.style.render(to_dict(entry)))
        self.assertEqual(expected, actual)

        # Edition Other Than the First
        entry = self.entries['Helfer1997']
        expected = "Helfer, M. E., Kempe, R. S., & Krugman, R. D. (1997). The battered child (5th ed.). Chicago, IL: University of Chicago Press."
        actual = self._remove_whitespaces(self.style.render(to_dict(entry)))
        self.assertEqual(expected, actual)

    def testinbook(self):
        # Article or Chapter in an Edited Book
        entry = self.entries['ONeil1992']
        expected = "O'Neil, J. M., & Egan, J. (1992). Men's and women's gender role journeys: Metaphor for healing, transition, and transformation. In Wainrib, B. R. (Ed.), Gender issues across the life cycle (pp. 107-123). New York, NY: Springer."
        actual = self._remove_whitespaces(self.style.render(to_dict(entry)))
        self.assertEqual(expected, actual)

    def testarticle(self):
        # Article in Journal Paginated by Volume
        entry = self.entries['Harlow1983']
        expected = "Harlow, H. F. (1983). Fundamentals for preparing psychology journal articles. Journal of Comparative and Physiological Psychology, 55, 893-896."
        actual = self._remove_whitespaces(self.style.render(to_dict(entry)))
        self.assertEqual(expected, actual)

        # Article in Journal Paginated by Issue
        entry = self.entries['Scruton1996']
        expected = "Scruton, R. (1996). The eclipse of listening. The New Criterion, 15(30), 5-13."
        actual = self._remove_whitespaces(self.style.render(to_dict(entry)))
        self.assertEqual(expected, actual)

    def testproceedings(self):
        entry = self.entries['Schnase1995']
        expected = "Schnase, J. L., & Cunnius, E. L. (Eds.). (1995). Proceedings from CSCL '95: The first international conference on computer support for collaborative learning. Mahwah, NJ: Erlbaum."
        actual = self._remove_whitespaces(self.style.render(to_dict(entry)))
        self.assertEqual(expected, actual)

    def testphdthesis(self):
        entry = self.entries['Doe2011']
        expected = "Doe, J. (2011). Title of dissertation. (Unpublished doctoral dissertation). Name of Institution, Location."
        actual = self._remove_whitespaces(self.style.render(to_dict(entry)))
        self.assertEqual(expected, actual)

    def testmastersthesis(self):
        entry = self.entries['Doe2010']
        expected = "Doe, J. (2010). Title of dissertation. (Unpublished master's dissertation). Name of Institution, Location."
        actual = self._remove_whitespaces(self.style.render(to_dict(entry)))
        self.assertEqual(expected, actual)

    def testincollection(self):
        entry = self.entries['Bergmann1993']
        expected = "Bergmann, P. G. (1993). Relativity. In The new encyclopedia britannica (Vol. 26, pp. 501-508). Chicago, IL: Encyclopedia Britannica."
        actual = self._remove_whitespaces(self.style.render(to_dict(entry)))
        self.assertEqual(expected, actual)

    def testtechreport(self):
        entry = self.entries['APA2000']
        expected = "American Psychiatric Association. (2000). Practice guidelines for the treatment of patients with eating disorders (2nd ed.). Washington, DC: Author ."
        actual = self._remove_whitespaces(self.style.render(to_dict(entry)))
        self.assertEqual(expected, actual)

    def testmisc(self):
        entry = self.entries['wiki']
        expected = 'Wikipedia (2011). <a href="http://en.wikipedia.org/w/index.php?title=BibTeX&oldid=406037891">BibTeX --- Wikipedia, the free encyclopedia</a>. [Online; accessed 26-February-2011].'
        actual = self._remove_whitespaces(self.style.render(to_dict(entry)))
        self.assertEqual(expected, actual)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
