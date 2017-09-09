#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import sys
import subprocess

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

# Globals and constants variables.

class Test__main__(TestCase):

    def testprograms(self):
        args = [sys.executable, '-m', 'pymontecarlo', '--programs']
        process = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = process.stderr.decode('ascii')
        self.assertTrue(out.startswith('Programs: '))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
