#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.program.config import Program
from pymontecarlo.input.converter import Converter
from pymontecarlo.runner.worker import Worker
from pymontecarlo.output.results import Results

# Globals and constants variables.

class DummyConverter(Converter):

    def _convert_beam(self, options):
        pass

    def _convert_geometry(self, options):
        pass

    def _convert_detectors(self, options):
        pass

    def _convert_limits(self, options):
        pass

    def _convert_models(self, options):
        pass

class DummyWorker(Worker):

    def create(self, options, outputdir):
        logging.info('Simulation created')

    def run(self, options, outputdir, workdir):
        self._status = 'Started'
        self._progress = 0.1

        logging.info('Simulation run')

        self._status = 'Completed'
        self._progress = 1.0

        return Results(options)

class DummyProgram(Program):

    def __init__(self):
        Program.__init__(self, 'Dummy', 'dummy', DummyConverter, DummyWorker)

class TestProgram(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.program = DummyProgram()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testname(self):
        self.assertEqual('Dummy', self.program.name)

    def testalias(self):
        self.assertEqual('dummy', self.program.alias)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
