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
from math import radians

# Third party modules.

# Local modules.
from pymontecarlo.io.casino2.exporter import Exporter

from pymontecarlo.input.base.options import Options
from pymontecarlo.input.base.detector import \
    (BackscatteredElectronEnergyDetector, TransmittedElectronEnergyDetector,
     BackscatteredElectronPolarAngularDetector, PhotonIntensityDetector,
     PhiRhoZDetector)
from pymontecarlo.input.base.limit import ShowersLimit
from pymontecarlo.input.base.material import Material
from pymontecarlo.input.base.geometry import GrainBoundaries, MultiLayers

# Globals and constants variables.

class TestCasino2Exporter(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.e = Exporter()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testto_cas_substrate(self):
        mat = Material('Mat1', {79: 0.5, 47: 0.5}, absorption_energy_electron=123)
        ops = Options()
        ops.beam.energy = 1234
        ops.beam.diameter = 25e-9
        ops.beam.origin = (100e-9, 0, 1)
        ops.geometry.material = mat
        ops.limits.add(ShowersLimit(5678))
        ops.detectors['bse'] = BackscatteredElectronEnergyDetector((0, 567), 123)
        ops.detectors['te'] = TransmittedElectronEnergyDetector((1, 568), 124)
        ops.detectors['bse polar'] = BackscatteredElectronPolarAngularDetector(125)
        ops.detectors['xrays'] = \
            PhotonIntensityDetector((radians(30), radians(40)), (0, radians(360.0)))
        ops.detectors['prz'] = \
            PhiRhoZDetector((radians(30), radians(40)), (0, radians(360.0)),
                            (-12.34, -56.78), 750)

        self.e.export(ops).write('/home/ppinard/vboxshare/test.sim')

    def testto_cas_grainboundaries(self):
        mat1 = Material('Mat1', {79: 0.5, 47: 0.5}, absorption_energy_electron=123)
        mat2 = Material('Mat2', {29: 0.5, 30: 0.5}, absorption_energy_electron=89)
        mat3 = Material('Mat3', {13: 0.5, 14: 0.5}, absorption_energy_electron=89)

        ops = Options()
        ops.beam.energy = 1234
        ops.beam.diameter = 25e-9
        ops.beam.origin = (100e-9, 0, 1)

        ops.geometry = GrainBoundaries(mat1, mat2)
        ops.geometry.add_layer(mat3, 25e-9)

        ops.limits.add(ShowersLimit(5678))

        self.e.export(ops).write('/home/ppinard/vboxshare/test_gb.sim')

    def testto_cas_multilayers1(self):
        mat1 = Material('Mat1', {79: 0.5, 47: 0.5}, absorption_energy_electron=123)
        mat2 = Material('Mat2', {29: 0.5, 30: 0.5}, absorption_energy_electron=89)
        mat3 = Material('Mat3', {13: 0.5, 14: 0.5}, absorption_energy_electron=89)

        ops = Options()
        ops.beam.energy = 1234
        ops.beam.diameter = 25e-9
        ops.beam.origin = (100e-9, 0, 1)

        ops.geometry = MultiLayers(mat1)
        ops.geometry.add_layer(mat2, 25e-9)
        ops.geometry.add_layer(mat3, 55e-9)

        ops.limits.add(ShowersLimit(5678))

        self.e.export(ops).write('/home/ppinard/vboxshare/test_ml.sim')

    def testto_cas_multilayers2(self):
        mat1 = Material('Mat1', {79: 0.5, 47: 0.5}, absorption_energy_electron=123)
        mat2 = Material('Mat2', {29: 0.5, 30: 0.5}, absorption_energy_electron=89)
        mat3 = Material('Mat3', {13: 0.5, 14: 0.5}, absorption_energy_electron=89)

        ops = Options()
        ops.beam.energy = 1234
        ops.beam.diameter = 25e-9
        ops.beam.origin = (100e-9, 0, 1)

        ops.geometry = MultiLayers(None)
        ops.geometry.add_layer(mat1, 15e-9)
        ops.geometry.add_layer(mat2, 25e-9)
        ops.geometry.add_layer(mat3, 55e-9)

        ops.limits.add(ShowersLimit(5678))

        self.e.export(ops).write('/home/ppinard/vboxshare/test_ml.sim')

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
