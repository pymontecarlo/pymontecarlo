#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging
from io import BytesIO
import xml.etree.ElementTree as etree

# Third party modules.

# Local modules.
from pymontecarlo.program._penelope.fileformat.options.material import MaterialXMLHandler
from pymontecarlo.program._penelope.options.material import \
    Material, InteractionForcing

# Globals and constants variables.
from pymontecarlo.options.particle import ELECTRON, PHOTON, POSITRON
from pymontecarlo.options.collision import HARD_BREMSSTRAHLUNG_EMISSION

class TestMaterialXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = MaterialXMLHandler()

        if1 = InteractionForcing(ELECTRON, HARD_BREMSSTRAHLUNG_EMISSION,
                                 - 4, (0.1, 1.0))
        self.obj = Material({'Cu': 1.0}, 'Pure Cu', density_kg_m3=8960.0,
                            elastic_scattering=(0.1, 0.2),
                            cutoff_energy_inelastic_eV=51.2,
                            cutoff_energy_bremsstrahlung_eV=53.4,
                            interaction_forcings=[if1],
                            maximum_step_length_m=123.456)

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        etree.register_namespace('mc-pen', 'http://pymontecarlo.sf.net/penelope')
        source = BytesIO(b'<mc-pen:material xmlns:mc-pen="http://pymontecarlo.sf.net/penelope" c1="0.1" c2="0.2" density="8960.0" dsmax="123.456" name="Pure Cu" wcc="51.2" wcr="53.4"><composition><element weightFraction="1.0" z="29" /></composition><interactionForcing collision="hard bremsstrahlung emission" forcer="-4" particle="electron" whigh="1.0" wlow="0.1" /></mc-pen:material>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertEqual('Pure Cu', str(obj))

        self.assertTrue(29 in obj.composition)
        self.assertAlmostEqual(1.0, obj.composition[29], 4)

        self.assertAlmostEqual(8.96, obj.density_kg_m3 / 1000.0, 4)

        self.assertAlmostEqual(50, obj.absorption_energy_eV[ELECTRON], 4)
        self.assertAlmostEqual(50, obj.absorption_energy_eV[PHOTON], 4)
        self.assertAlmostEqual(50, obj.absorption_energy_eV[POSITRON], 4)

        self.assertAlmostEqual(0.1, obj.elastic_scattering[0], 4)
        self.assertAlmostEqual(0.2, obj.elastic_scattering[1], 4)

        self.assertAlmostEqual(51.2, obj.cutoff_energy_inelastic_eV, 4)
        self.assertAlmostEqual(53.4, obj.cutoff_energy_bremsstrahlung_eV, 4)

        self.assertEqual(1, len(obj.interaction_forcings))
        if1 = list(obj.interaction_forcings)[0]
        self.assertIs(ELECTRON, if1.particle)
        self.assertIs(HARD_BREMSSTRAHLUNG_EMISSION, if1.collision)
        self.assertAlmostEqual(-4, if1.forcer, 6)
        self.assertAlmostEqual(0.1, if1.weight[0], 6)
        self.assertAlmostEqual(1.0, if1.weight[1], 6)

        self.assertAlmostEqual(123.456, obj.maximum_step_length_m, 4)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        self.assertEqual('Pure Cu', element.get('name'))

        children = element.find('composition')
        self.assertEqual(1, len(children))
        self.assertEqual(29, int(children[0].get('z')))

        self.assertAlmostEqual(8.96, float(element.get('density')) / 1000.0, 4)

        self.assertAlmostEqual(0.1, float(element.get('c1')), 4)
        self.assertAlmostEqual(0.2, float(element.get('c2')), 4)

        self.assertAlmostEqual(51.2, float(element.get('wcc')), 4)
        self.assertAlmostEqual(53.4, float(element.get('wcr')), 4)

        subelement = element.find('interactionForcing')
        self.assertEqual('electron', subelement.get('particle'))
        self.assertEqual('hard bremsstrahlung emission', subelement.get('collision'))
        self.assertAlmostEqual(-4.0, float(subelement.get('forcer')), 4)
        self.assertAlmostEqual(0.1, float(subelement.get('wlow')), 4)
        self.assertAlmostEqual(1.0, float(subelement.get('whigh')), 4)

        self.assertAlmostEqual(123.456, float(element.get('dsmax')), 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
