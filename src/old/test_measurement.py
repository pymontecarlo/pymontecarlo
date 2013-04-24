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

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.reconstruction.measurement import Measurement

from pymontecarlo.input.options import Options
from pymontecarlo.input.geometry import Substrate
from pymontecarlo.input.detector import PhotonIntensityDetector
from pymontecarlo.input.material import Material, pure
from pymontecarlo.output.results import Results
from pymontecarlo.output.result import PhotonIntensityResult, create_intensity_dict
from pymontecarlo.util.transition import Ka, La

# Globals and constants variables.

class TestMeasurement(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        baseops = Options()
        baseops.detectors['xray'] = PhotonIntensityDetector((0, 1), (0, 3))

        self.m = Measurement(baseops)
        self.m.add_kratio(Ka(29), 0.2470, 0.004)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testadd_kratio(self):
        standard = Material('U90', {92: 0.9, 49: 0.1})
        self.m.add_kratio(La(92), 0.5, standard=standard)

        self.assertTrue(self.m.has_kratio(La(92)))
        self.assertAlmostEqual(0.5, self.m.get_kratios()[1], 4)

        self.m.add_kratio(Ka(13), 0.2, unc=0.125)

        self.assertTrue(self.m.has_kratio(Ka(13)))
        self.assertAlmostEqual(0.2, self.m.get_kratios()[0], 4)

        self.assertRaises(ValueError, self.m.add_kratio, La(92), 0.1)
        self.assertRaises(ValueError, self.m.add_kratio, Ka(14), -0.1)

    def testremove_kratio(self):
        self.m.remove_kratio(Ka(29))
        self.assertFalse(self.m.has_kratio(Ka(29)))
        self.assertEqual(0, len(self.m.get_kratios()))

    def testclear_kratios(self):
        self.m.clear_kratios()
        self.assertEqual(0, len(self.m.get_kratios()))

    def testhas_kratio(self):
        self.assertTrue(self.m.has_kratio(Ka(29)))
        self.assertFalse(self.m.has_kratio(La(29)))

    def testget_kratios(self):
        kratios = self.m.get_kratios()

        self.assertEqual(1, len(kratios))
        self.assertAlmostEqual(0.247, kratios[0], 4)

    def testfrom_xml(self):
        element = self.m.to_xml()
        m = Measurement.from_xml(element)

        kratios = m.get_kratios()
        self.assertEqual(1, len(kratios))
        self.assertAlmostEqual(0.247, kratios[0], 4)

    def testto_xml(self):
        element = self.m.to_xml()
        self.assertEqual(1, len(element.findall('kratio')))

    def testcreate_standard_options(self):
        list_options = self.m.create_standard_options('std')
        self.assertEqual(1, len(list_options))

    def testextract_standard_intensities(self):
        list_options = self.m.create_standard_options('std')
        stdoptions = list_options[0]

        intensities = create_intensity_dict(Ka(29), et=(8.0, 0.0))
        results = {'xray': PhotonIntensityResult(intensities)}
        stdresults = Results(stdoptions, results)

        dict_results = {'std+Cu Ka': stdresults}
        stdintensities = self.m.extract_standard_intensities('std', dict_results)

        self.assertEqual(1, len(stdintensities))
        self.assertAlmostEqual(8.0, stdintensities[0], 4)

    def testcreate_unknown_options(self):
        unkgeometry = Substrate(pure(49))
        options = self.m.create_unknown_options('meas', unkgeometry)
        self.assertEqual('meas', options.name)

    def testextract_unknown_intensities(self):
        unkgeometry = Substrate(pure(49))
        options = self.m.create_unknown_options('meas', unkgeometry)

        intensities = create_intensity_dict(Ka(29), et=(4.0, 0.0))
        results = Results(options, {'xray': PhotonIntensityResult(intensities)})

        unkintensities = self.m.extract_unknown_intensities(results)

        self.assertEqual(1, len(unkintensities))
        self.assertAlmostEqual(4.0, unkintensities[0], 4)



if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

