#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging
import os
import tempfile
import shutil

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.fileformat.options.updater import Updater

# Globals and constants variables.

class TestUpdater(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.tmpdir = tempfile.mkdtemp()
        self.testdata = os.path.join(os.path.dirname(__file__), '..', '..', 'testdata')
        self.updater = Updater()

    def tearDown(self):
        TestCase.tearDown(self)

        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testupdate_noversion0(self):
        src = os.path.join(self.testdata, 'oldoptions0.xml')
        dst = os.path.join(self.tmpdir, 'oldoptions0.xml')
        shutil.copy(src, dst)

        self.updater.update(dst)

    def testupdate_noversion1(self):
        src = os.path.join(self.testdata, 'oldoptions1.xml')
        dst = os.path.join(self.tmpdir, 'oldoptions1.xml')
        shutil.copy(src, dst)

        self.updater.update(dst)

    def testupdate_noversion2(self):
        src = os.path.join(self.testdata, 'oldoptions2.xml')
        dst = os.path.join(self.tmpdir, 'oldoptions2.xml')
        shutil.copy(src, dst)

        self.updater.update(dst)

    def testupdate_noversion3(self):
        src = os.path.join(self.testdata, 'oldoptions3.xml')
        dst = os.path.join(self.tmpdir, 'oldoptions3.xml')
        shutil.copy(src, dst)

        self.updater.update(dst)

    def testupdate_noversion4(self):
        src = os.path.join(self.testdata, 'oldoptions4.xml')
        dst = os.path.join(self.tmpdir, 'oldoptions4.xml')
        shutil.copy(src, dst)

        self.updater.update(dst)

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
