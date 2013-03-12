#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging
import tempfile
import shutil
import warnings
from math import radians

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.input.particle import ELECTRON
from pymontecarlo.input.collision import HARD_ELASTIC
from pymontecarlo.input.options import Options
from pymontecarlo.input.limit import TimeLimit
from pymontecarlo.input.detector import \
    PhotonIntensityDetector, PhotonSpectrumDetector, PhotonDepthDetector
from pymontecarlo.program.penepma.input.converter import Converter
from pymontecarlo.program._penelope.input.interactionforcing import InteractionForcing
from pymontecarlo.program.penepma.input.exporter import Exporter, ExporterException

# Globals and constants variables.
from pymontecarlo.program.penepma.input.exporter import \
    MAX_PHOTON_DETECTORS, MAX_PRZ

warnings.simplefilter("always")

class TestPenelopeExporter(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.tmpdir = tempfile.mkdtemp()

        self.c = Converter()
        self.e = Exporter()

    def tearDown(self):
        TestCase.tearDown(self)

        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testskeleton(self):
        self.assertTrue(True)

    def testexport(self):
        # Create
        ops = Options(name='test1')
        ops.beam.energy_eV = 30e3
        ops.detectors['x-ray'] = \
            PhotonIntensityDetector((radians(35), radians(45)), (0, radians(360.0)))
        ops.detectors['spectrum'] = \
            PhotonSpectrumDetector((radians(35), radians(45)), (0, radians(360.0)), (0, 1000), 500)
        ops.detectors['prz'] = \
            PhotonDepthDetector((radians(0), radians(90)), (0, radians(360.0)), 500)
        ops.limits.add(TimeLimit(100))

        # Export
        self.c.convert(ops)
        self.e.export(ops, self.tmpdir)

    def test_append_photon_detectors_maxlimit(self):
        ops = Options()
        ops.limits.add(TimeLimit(100))

        for i in range(MAX_PHOTON_DETECTORS + 1):
            ops.detectors['det%i' % i] = \
                PhotonSpectrumDetector((radians(i), radians(45)), (0, radians(360.0)),
                                       (0, 1000), 500)

        self.c.convert(ops)
        self.assertRaises(ExporterException, self.e.export, ops, self.tmpdir)

    def test_append_photon_detectors_maxchannels(self):
        ops = Options()
        ops.limits.add(TimeLimit(100))
        ops.detectors['spectrum'] = \
            PhotonSpectrumDetector((radians(35), radians(45)), (0, radians(360.0)),
                                   (0, 1000), 50000)

        self.c.convert(ops)

        with warnings.catch_warnings(record=True) as ws:
            self.e.export(ops, self.tmpdir)

        self.assertEqual(1, len(ws))

    def test_append_phirhoz_distribution_channels(self):
        ops = Options()
        ops.beam.energy_eV = 30e3
        ops.limits.add(TimeLimit(100))
        ops.detectors['prz1'] = \
            PhotonDepthDetector((radians(35), radians(45)), (0, radians(360.0)), 500)
        ops.detectors['prz2'] = \
            PhotonDepthDetector((radians(35), radians(45)), (0, radians(360.0)), 500)

        self.c.convert(ops)

        with warnings.catch_warnings(record=True) as ws:
            self.e.export(ops, self.tmpdir)

        self.assertEqual(2, len(ws))

    def test_append_phirhoz_distribution_maxlimit(self):
        ops = Options()
        ops.beam.energy_eV = 30e3
        ops.limits.add(TimeLimit(100))

        for i in range(MAX_PRZ + 1):
            ops.detectors['det%i' % i] = \
                PhotonDepthDetector((radians(i), radians(45)), (0, radians(360.0)), 500)

        self.c.convert(ops)
        self.assertRaises(ExporterException, self.e.export, ops, self.tmpdir)

    def test_append_phirhoz_distribution_restrain_transitions(self):
        ops = Options()
        ops.beam.energy_eV = 30e3
        ops.limits.add(TimeLimit(100))

        for i in range(10):
            ops.detectors['det%i' % i] = \
                PhotonDepthDetector((radians(i), radians(45)), (0, radians(360.0)), 500)

        self.c.convert(ops)

        with warnings.catch_warnings(record=True) as ws:
            self.e.export(ops, self.tmpdir)

        self.assertEqual(10 + 1, len(ws))

    def testinteraction_forcing(self):
        ops = Options()
        ops.beam.energy_eV = 30e3
        ops.limits.add(TimeLimit(100))

        self.c.convert(ops)

        intfor = InteractionForcing(ELECTRON, HARD_ELASTIC, -40)
        ops.geometry.body.interaction_forcings.add(intfor)

        self.e.export(ops, self.tmpdir)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
