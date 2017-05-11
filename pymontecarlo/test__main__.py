#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import os
import sys
import subprocess

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.util.path import get_config_dir
from pymontecarlo._settings import Settings

# Globals and constants variables.

class Test__main__(TestCase):

    def setUp(self):
        super().setUp()

        # Exchange settings.h5
        self.filepath = os.path.join(get_config_dir(), Settings.DEFAULT_FILENAME)

        if os.path.exists(self.filepath):
            self.filepath_backup = self.filepath + '.backup'
            os.rename(self.filepath, self.filepath_backup)
        else:
            self.filepath_backup = None

        settings = Settings()
        settings.write(self.filepath)

    def tearDown(self):
        super().tearDown()

        os.remove(self.filepath)

        if self.filepath_backup:
            os.rename(self.filepath_backup, self.filepath)

    def testprograms(self):
        args = [sys.executable, '-m', 'pymontecarlo', '--programs']
        process = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = process.stderr.decode('ascii')
        self.assertEqual('Program', out[:7])

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
