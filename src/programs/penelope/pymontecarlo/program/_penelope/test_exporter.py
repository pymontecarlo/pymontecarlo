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
from nose.plugins.attrib import attr

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.settings import get_settings

from pymontecarlo.options.options import Options
from pymontecarlo.options.geometry import \
    Substrate, Inclusion, HorizontalLayers, VerticalLayers, Sphere #, Cuboids2D
from pymontecarlo.options.limit import TimeLimit

from pymontecarlo.program._penelope.options.material import Material
from pymontecarlo.program._penelope.converter import Converter
from pymontecarlo.program._penelope.exporter import Exporter
import penelopelib.pengeom as pengeom

# Globals and constants variables.

class TestPenelopeExporter(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.tmpdir = tempfile.mkdtemp()
        self.e = Exporter(get_settings().penepma.pendbase)
        self.c = Converter()

    def tearDown(self):
        TestCase.tearDown(self)

        shutil.rmtree(self.tmpdir)

    def testskeleton(self):
        self.assertTrue(True)

    @attr('slow')
    def testexport_substrate(self):
        # Create
        mat1 = Material({79: 0.5, 47: 0.5}, 'mat')

        ops = Options()
        ops.geometry = Substrate(mat1)
        ops.limits.add(TimeLimit(100))

        self.c._convert_geometry(ops)
        self.e.export_geometry(ops.geometry, self.tmpdir)

        # Test
        geofilepath = os.path.join(self.tmpdir, 'substrate.geo')
        repfilepath = os.path.join(self.tmpdir, 'geometry.rep')
        nmat, nbody = pengeom.init(geofilepath, repfilepath)

        self.assertEqual(1, nmat)
        self.assertEqual(2, nbody)

        matfilepath = os.path.join(self.tmpdir, 'mat1.mat')
        self.assertTrue(os.path.exists(matfilepath))

    @attr('slow')
    def testexport_inclusion(self):
        # Create
        mat1 = Material({79: 0.5, 47: 0.5}, 'mat')
        mat2 = Material({29: 0.5, 30: 0.5}, 'mat')

        ops = Options()
        ops.geometry = Inclusion(mat1, mat2, 0.01)
        ops.limits.add(TimeLimit(100))

        self.c._convert_geometry(ops)
        self.e.export_geometry(ops.geometry, self.tmpdir)

        # Test
        geofilepath = os.path.join(self.tmpdir, 'inclusion.geo')
        repfilepath = os.path.join(self.tmpdir, 'geometry.rep')
        nmat, nbody = pengeom.init(geofilepath, repfilepath)

        self.assertEqual(2, nmat)
        self.assertEqual(3, nbody)

        matfilepath = os.path.join(self.tmpdir, 'mat1.mat')
        self.assertTrue(os.path.exists(matfilepath))

        matfilepath = os.path.join(self.tmpdir, 'mat2.mat')
        self.assertTrue(os.path.exists(matfilepath))

    @attr('slow')
    def testexport_horizontal_layers(self):
        # Create
        mat1 = Material({79: 0.5, 47: 0.5}, 'mat1')
        mat2 = Material({29: 0.5, 30: 0.5}, 'mat2')
        mat3 = Material({13: 0.5, 14: 0.5}, 'mat3')

        ops = Options()
        ops.beam.energy_eV = 1234
        ops.beam.diameter_m = 25e-9
        ops.beam.origin_m = (100e-9, 0, 1)

        ops.geometry = HorizontalLayers(mat1)
        ops.geometry.add_layer(mat2, 52e-9)
        ops.geometry.add_layer(mat3, 25e-9)

        ops.limits.add(TimeLimit(100))

        self.c._convert_geometry(ops)
        self.e.export_geometry(ops.geometry, self.tmpdir)

        # Test
        geofilepath = os.path.join(self.tmpdir, 'horizontallayers.geo')
        repfilepath = os.path.join(self.tmpdir, 'geometry.rep')
        nmat, nbody = pengeom.init(geofilepath, repfilepath)

        self.assertEqual(3, nmat)
        self.assertEqual(6, nbody)

        matfilepath = os.path.join(self.tmpdir, 'mat1.mat')
        self.assertTrue(os.path.exists(matfilepath))

        matfilepath = os.path.join(self.tmpdir, 'mat2.mat')
        self.assertTrue(os.path.exists(matfilepath))

        matfilepath = os.path.join(self.tmpdir, 'mat3.mat')
        self.assertTrue(os.path.exists(matfilepath))

    @attr('slow')
    def testexport_vertical_layers(self):
        # Create
        mat1 = Material({79: 0.5, 47: 0.5}, 'mat1')
        mat2 = Material({29: 0.5, 30: 0.5}, 'mat2')
        mat3 = Material({13: 0.5, 14: 0.5}, 'mat3')

        ops = Options()
        ops.beam.energy_eV = 1234
        ops.beam.diameter_m = 25e-9
        ops.beam.origin_m = (100e-9, 0, 1)

        ops.geometry = VerticalLayers(mat1, mat2)
        ops.geometry.add_layer(mat3, 5e-3)

        ops.limits.add(TimeLimit(100))

        self.c._convert_geometry(ops)
        self.e.export_geometry(ops.geometry, self.tmpdir)

        # Test
        geofilepath = os.path.join(self.tmpdir, 'verticallayers.geo')
        repfilepath = os.path.join(self.tmpdir, 'geometry.rep')
        nmat, nbody = pengeom.init(geofilepath, repfilepath)

        self.assertEqual(3, nmat)
        self.assertEqual(4, nbody)

        matfilepath = os.path.join(self.tmpdir, 'mat1.mat')
        self.assertTrue(os.path.exists(matfilepath))

        matfilepath = os.path.join(self.tmpdir, 'mat2.mat')
        self.assertTrue(os.path.exists(matfilepath))

        matfilepath = os.path.join(self.tmpdir, 'mat3.mat')
        self.assertTrue(os.path.exists(matfilepath))

    @attr('slow')
    def testexport_sphere(self):
        # Create
        mat1 = Material({79: 0.5, 47: 0.5}, 'mat')

        ops = Options()
        ops.geometry = Sphere(mat1, 0.01)
        ops.limits.add(TimeLimit(100))

        self.c._convert_geometry(ops)
        self.e.export_geometry(ops.geometry, self.tmpdir)

        # Test
        geofilepath = os.path.join(self.tmpdir, 'sphere.geo')
        repfilepath = os.path.join(self.tmpdir, 'geometry.rep')
        nmat, nbody = pengeom.init(geofilepath, repfilepath)

        self.assertEqual(1, nmat)
        self.assertEqual(2, nbody)

        matfilepath = os.path.join(self.tmpdir, 'mat1.mat')
        self.assertTrue(os.path.exists(matfilepath))

#    @attr('slow')
#    def testexport_cuboids2d(self):
#        # Create
#        mat1 = Material('mat', {79: 0.5, 47: 0.5})
#
#        ops = Options()
#
#        ops.geometry = Cuboids2D(3, 3, 0.0001, 0.0002)
#        ops.geometry.material[-1, -1] = mat1
#        ops.geometry.material[-1, 0] = mat1
#        ops.geometry.material[-1, 1] = mat1
#        ops.geometry.material[0, -1] = mat1
#        ops.geometry.material[0, 0] = mat1
#        ops.geometry.material[0, 1] = mat1
#        ops.geometry.material[1, -1] = mat1
#        ops.geometry.material[1, 0] = mat1
#        ops.geometry.material[1, 1] = mat1
#
#        ops.limits.add(TimeLimit(100))
#
#        self.c._convert_geometry(ops)
#        self.e.export_geometry(ops.geometry, self.tmpdir)
#
#        # Test
#        geofilepath = os.path.join(self.tmpdir, 'cuboids2d.geo')
#        repfilepath = os.path.join(self.tmpdir, 'geometry.rep')
#        nmat, nbody = pengeom.init(geofilepath, repfilepath)
#
#        self.assertEqual(1, nmat)
#        self.assertEqual(10, nbody)
#
#        matfilepath = os.path.join(self.tmpdir, 'mat1.mat')
#        self.assertTrue(os.path.exists(matfilepath))


if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
