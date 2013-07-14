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
from pyxray.transition import Ka

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.reconstruction.experiment import Experiment
from pymontecarlo.reconstruction.measurement import Measurement
from pymontecarlo.reconstruction.parameter import Parameter

from pymontecarlo.input.options import Options
from pymontecarlo.input.geometry import MultiLayers
from pymontecarlo.input.material import Material, pure
from pymontecarlo.input.detector import PhotonIntensityDetector
from pymontecarlo.output.results import Results
from pymontecarlo.output.result import PhotonIntensityResult, create_intensity_dict

# Globals and constants variables.

class TestExperiment(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        geometry = MultiLayers(pure(29))
        geometry.add_layer(Material("AuPd", {79: 0.5, 46: 0.5}), 100e-9)

        baseops = Options()
        baseops.detectors['xray'] = PhotonIntensityDetector((0, 1), (0, 3))
        meas = Measurement(baseops)
        meas.add_kratio(Ka(29), 0.2470, 0.004)

        getter = lambda geometry: geometry.layers[0].thickness_m
        setter = lambda geometry, val: setattr(geometry.layers[0], 'thickness_m', val)
        param = Parameter(getter, setter, 100e-9, 10e-9, 500e-9)

        self.exp = Experiment(geometry, [meas], [param])

    def tearDown(self):
        TestCase.tearDown(self)

    def testreference_kratios(self):
        kratios = self.exp.reference_kratios
        self.assertEqual(1, len(kratios))
        self.assertAlmostEqual(0.2470, kratios[0], 4)

    def testparameters_initial_values(self):
        vals = self.exp.parameters_initial_values
        self.assertEqual(1, len(vals))
        self.assertAlmostEqual(100e-9, vals[0], 13)

    def testparameters_constraints(self):
        constraints = self.exp.parameters_constraints
        self.assertEqual(1, len(constraints))
        self.assertAlmostEqual(10e-9, constraints[0][0], 13)
        self.assertAlmostEqual(500e-9, constraints[0][1], 13)

    def testcreate_standard_options(self):
        list_options = self.exp.create_standard_options()
        self.assertEqual(1, len(list_options))
        self.assertEqual('0+Cu Ka', list_options[0].name)

    def testextract_standard_intensities(self):
        list_options = self.exp.create_standard_options()
        stdoptions = list_options[0]

        intensities = create_intensity_dict(Ka(29), et=(8.0, 0.0))
        stdresults = Results(stdoptions,
                             {'xray': PhotonIntensityResult(intensities)})

        stdintensities = self.exp.extract_standard_intensities([stdresults])

        self.assertEqual(1, len(stdintensities))
        self.assertAlmostEqual(8.0, stdintensities[0], 4)

    def testcreate_geometry(self):
        values = [200e-9]
        geometry = self.exp.create_geometry(values)
        self.assertAlmostEqual(200e-9, geometry.layers[0].thickness_m, 13)

    def testcreate_unknown_options(self):
        list_values = [(200e-9,), (250e-9,)]
        list_options = self.exp.create_unknown_options(list_values)
        self.assertEqual(2, len(list_options))

        unkoptions = list_options[0]
        self.assertAlmostEqual(200e-9, unkoptions.geometry.layers[0].thickness_m, 13)

        unkoptions = list_options[1]
        self.assertAlmostEqual(250e-9, unkoptions.geometry.layers[0].thickness_m, 13)

    def testextract_kratios(self):
        list_values = [(200e-9,), (250e-9,)]
        list_options = self.exp.create_unknown_options(list_values)

        intensities = create_intensity_dict(Ka(29), et=(4.0, 0.0))
        results1 = Results(list_options[0],
                           {'xray': PhotonIntensityResult(intensities)})

        intensities = create_intensity_dict(Ka(29), et=(8.0, 0.0))
        results2 = Results(list_options[1],
                           {'xray': PhotonIntensityResult(intensities)})

        intensities = self.exp.extract_unknown_intensities([results1, results2])

        self.assertEqual(2, len(intensities))
        self.assertAlmostEqual(4.0, intensities[0][0], 4)
        self.assertAlmostEqual(8.0, intensities[1][0], 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
