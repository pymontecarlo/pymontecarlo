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

from pymontecarlo.results.updater import Updater

# Globals and constants variables.

class TestUpdater(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.tmpdir = tempfile.mkdtemp()
        self.testdata = os.path.join(os.path.dirname(__file__), '../testdata')
        self.updater = Updater()

    def tearDown(self):
        TestCase.tearDown(self)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testupdate_noversion0(self):
        src = os.path.join(self.testdata, 'oldresults0.xml')
        dst = os.path.join(self.tmpdir, 'oldresults0.xml')
        shutil.copy(src, dst)

        src = os.path.join(self.testdata, 'oldresults0.zip')
        dst = os.path.join(self.tmpdir, 'oldresults0.zip')
        shutil.copy(src, dst)

        self.updater.update(dst)

    def testupdate_noversion1(self):
        src = os.path.join(self.testdata, 'oldresults1.xml')
        dst = os.path.join(self.tmpdir, 'oldresults1.xml')
        shutil.copy(src, dst)

        src = os.path.join(self.testdata, 'oldresults1.zip')
        dst = os.path.join(self.tmpdir, 'oldresults1.zip')
        shutil.copy(src, dst)

        self.updater.update(dst)

    def testupdate_version2(self):
        src = os.path.join(self.testdata, 'oldresults2.xml')
        dst = os.path.join(self.tmpdir, 'oldresults2.xml')
        shutil.copy(src, dst)

        src = os.path.join(self.testdata, 'oldresults2.zip')
        dst = os.path.join(self.tmpdir, 'oldresults2.zip')
        shutil.copy(src, dst)

        self.updater.update(dst)

    def testupdate_version3(self):
        src = os.path.join(self.testdata, 'oldresults3.zip')
        dst = os.path.join(self.tmpdir, 'oldresults3.zip')
        shutil.copy(src, dst)

        self.updater.update(dst)

    def testupdate_version4(self):
        src = os.path.join(self.testdata, 'oldresults4.h5')
        dst = os.path.join(self.tmpdir, 'oldresults4.h5')
        shutil.copy(src, dst)

        self.updater.update(dst)

    def testupdate_version5(self):
        src = os.path.join(self.testdata, 'oldresults5.h5')
        dst = os.path.join(self.tmpdir, 'oldresults5.h5')
        shutil.copy(src, dst)

        self.updater.update(dst)

    def testupdate_java(self):
        src = os.path.join(self.testdata, 'oldresults_java.h5')
        dst = os.path.join(self.tmpdir, 'oldresults_java.h5')
        shutil.copy(src, dst)

        self.updater.update(dst)

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
