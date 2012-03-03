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
import os
import tempfile
import shutil

# Third party modules.

# Local modules.
from pymontecarlo import settings
from pymontecarlo.input.base.options import Options
from pymontecarlo.input.base.geometry import Substrate, Inclusion, MultiLayers, GrainBoundaries
from pymontecarlo.input.penelope.converter import Converter
from pymontecarlo.input.penelope.material import Material
from pymontecarlo.io.penelope.exporter import Exporter
import pymontecarlo.lib.penelope.wrapper as wrapper

# Globals and constants variables.

class TestPenelopeExporter(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.tmpdir = tempfile.mkdtemp()
        self.e = Exporter(settings.penelope.pendbase)
        self.c = Converter()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

        shutil.rmtree(self.tmpdir)

    def testskeleton(self):
        self.assertTrue(True)

    def testexport_geometry_substrate(self):
        # Create
        mat1 = Material('mat', {79: 0.5, 47: 0.5})

        ops = Options()
        ops.geometry = Substrate(mat1)

        self.c.convert(ops)
        self.e.export_geometry(ops, self.tmpdir)

        # Test
        geofilepath = os.path.join(self.tmpdir, 'substrate.geo')
        repfilepath = os.path.join(self.tmpdir, 'geometry.rep')
        nmat, nbody = wrapper.geomin(geofilepath, repfilepath)

        self.assertEqual(1, nmat)
        self.assertEqual(2, nbody)

        matfilepath = os.path.join(self.tmpdir, 'mat1.mat')
        self.assertTrue(os.path.exists(matfilepath))

    def testexport_geometry_inclusion(self):
        # Create
        mat1 = Material('mat', {79: 0.5, 47: 0.5})
        mat2 = Material('mat', {29: 0.5, 30: 0.5})

        ops = Options()
        ops.geometry = Inclusion(mat1, mat2, 0.01)

        self.c.convert(ops)
        self.e.export_geometry(ops, self.tmpdir)

        # Test
        geofilepath = os.path.join(self.tmpdir, 'inclusion.geo')
        repfilepath = os.path.join(self.tmpdir, 'geometry.rep')
        nmat, nbody = wrapper.geomin(geofilepath, repfilepath)

        self.assertEqual(2, nmat)
        self.assertEqual(3, nbody)

        matfilepath = os.path.join(self.tmpdir, 'mat1.mat')
        self.assertTrue(os.path.exists(matfilepath))

        matfilepath = os.path.join(self.tmpdir, 'mat2.mat')
        self.assertTrue(os.path.exists(matfilepath))

    def testexport_geometry_multilayers(self):
        # Create
        mat1 = Material('mat1', {79: 0.5, 47: 0.5})
        mat2 = Material('mat2', {29: 0.5, 30: 0.5})
        mat3 = Material('mat3', {13: 0.5, 14: 0.5})

        ops = Options()
        ops.beam.energy_eV = 1234
        ops.beam.diameter_m = 25e-9
        ops.beam.origin_m = (100e-9, 0, 1)

        ops.geometry = MultiLayers(mat1)
        ops.geometry.add_layer(mat2, 52e-9)
        ops.geometry.add_layer(mat3, 25e-9)

        self.c.convert(ops)
        self.e.export_geometry(ops, self.tmpdir)

        # Test
        geofilepath = os.path.join(self.tmpdir, 'multilayers.geo')
        repfilepath = os.path.join(self.tmpdir, 'geometry.rep')
        nmat, nbody = wrapper.geomin(geofilepath, repfilepath)

        self.assertEqual(3, nmat)
        self.assertEqual(6, nbody)

        matfilepath = os.path.join(self.tmpdir, 'mat1.mat')
        self.assertTrue(os.path.exists(matfilepath))

        matfilepath = os.path.join(self.tmpdir, 'mat2.mat')
        self.assertTrue(os.path.exists(matfilepath))

        matfilepath = os.path.join(self.tmpdir, 'mat3.mat')
        self.assertTrue(os.path.exists(matfilepath))

    def testexport_geometry_grainboundaries(self):
        # Create
        mat1 = Material('mat1', {79: 0.5, 47: 0.5})
        mat2 = Material('mat2', {29: 0.5, 30: 0.5})
        mat3 = Material('mat3', {13: 0.5, 14: 0.5})

        ops = Options()
        ops.beam.energy_eV = 1234
        ops.beam.diameter_m = 25e-9
        ops.beam.origin_m = (100e-9, 0, 1)

        ops.geometry = GrainBoundaries(mat1, mat2)
        ops.geometry.add_layer(mat3, 5e-3)

        self.c.convert(ops)
        self.e.export_geometry(ops, self.tmpdir)

        # Test
        geofilepath = os.path.join(self.tmpdir, 'grainboundaries.geo')
        repfilepath = os.path.join(self.tmpdir, 'geometry.rep')
        nmat, nbody = wrapper.geomin(geofilepath, repfilepath)

        self.assertEqual(3, nmat)
        self.assertEqual(4, nbody)

        matfilepath = os.path.join(self.tmpdir, 'mat1.mat')
        self.assertTrue(os.path.exists(matfilepath))

        matfilepath = os.path.join(self.tmpdir, 'mat2.mat')
        self.assertTrue(os.path.exists(matfilepath))

        matfilepath = os.path.join(self.tmpdir, 'mat3.mat')
        self.assertTrue(os.path.exists(matfilepath))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
