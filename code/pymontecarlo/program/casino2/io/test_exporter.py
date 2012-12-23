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
from operator import attrgetter

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.program.casino2.io.exporter import Exporter, ExporterException

from pymontecarlo.input.options import Options
from pymontecarlo.input.detector import \
    (BackscatteredElectronEnergyDetector, TransmittedElectronEnergyDetector,
     BackscatteredElectronPolarAngularDetector, PhotonIntensityDetector,
     PhiRhoZDetector)
from pymontecarlo.input.limit import ShowersLimit
from pymontecarlo.input.material import Material
from pymontecarlo.input.geometry import GrainBoundaries, MultiLayers
from pymontecarlo.input.model import \
    (ELASTIC_CROSS_SECTION, IONIZATION_CROSS_SECTION, IONIZATION_POTENTIAL,
     RANDOM_NUMBER_GENERATOR, DIRECTION_COSINE)

from casinoTools.FileFormat.casino2.SimulationOptions import \
    (DIRECTION_COSINES_SOUM, CROSS_SECTION_MOTT_EQUATION,
     IONIZATION_CROSS_SECTION_GRYZINSKI, IONIZATION_POTENTIAL_HOVINGTON,
     RANDOM_NUMBER_GENERATOR_MERSENNE_TWISTER, ENERGY_LOSS_JOY_LUO)

# Globals and constants variables.

class TestCasino2Exporter(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.e = Exporter()

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testexport_substrate(self):
        # Create options
        mat = Material('Mat1', {79: 0.5, 47: 0.5}, absorption_energy_electron_eV=123)
        ops = Options()
        ops.beam.energy_eV = 1234
        ops.beam.diameter_m = 25e-9
        ops.beam.origin_m = (100e-9, 0, 1)
        ops.geometry.material = mat
        ops.limits.add(ShowersLimit(5678))
        ops.detectors['bse'] = BackscatteredElectronEnergyDetector((0, 567), 123)
        ops.detectors['te'] = TransmittedElectronEnergyDetector((1, 568), 124)
        ops.detectors['bse polar'] = BackscatteredElectronPolarAngularDetector(125)
        ops.detectors['xrays'] = \
            PhotonIntensityDetector((radians(30), radians(40)), (0, radians(360.0)))
        ops.detectors['prz'] = \
            PhiRhoZDetector((radians(30), radians(40)), (0, radians(360.0)), 750)

        # Export to CAS
        casfile = self.e.export(ops)

        # Test
        simdata = casfile.getOptionSimulationData()
        simops = simdata.getSimulationOptions()
        regionops = simdata.getRegionOptions()

        self.assertAlmostEqual(1.234, simops.getIncidentEnergy_keV(0), 4)
        self.assertAlmostEqual(34.93392125, simops.Beam_Diameter, 4) # FWHM
        self.assertAlmostEqual(100.0, simops._positionStart_nm, 4)

        self.assertEqual(1, regionops.getNumberRegions())
        region = regionops.getRegion(0)
        elements = map(attrgetter('Z'), region.getElements())
        self.assertAlmostEqual(mat.density_kg_m3, region.Rho, 4)
        self.assertEqual('Mat1', region.Name)
        self.assertEqual(2, len(elements))
        self.assertTrue(79 in elements)
        self.assertTrue(47 in elements)
        self.assertAlmostEqual(0.123, simops.Eminimum, 3)

        self.assertEqual(5678, simops.getNumberElectrons())

        self.assertTrue(simops.FDenr)
        self.assertFalse(simops.FDenrLog)
        self.assertEqual(123, simops.NbPointDENR)
        self.assertAlmostEqual(0.0, simops.DenrMin, 3)
        self.assertAlmostEqual(0.567, simops.DenrMax, 3)

        self.assertTrue(simops.FDent)
        self.assertFalse(simops.FDentLog)
        self.assertEqual(124, simops.NbPointDENT)
        self.assertAlmostEqual(0.001, simops.DentMin, 3)
        self.assertAlmostEqual(0.568, simops.DentMax, 3)

        self.assertTrue(simops.FDbang)
        self.assertFalse(simops.FDbangLog)
        self.assertEqual(125, simops.NbPointDBANG)
        self.assertAlmostEqual(-90.0, simops.DbangMin, 4)
        self.assertAlmostEqual(90.0, simops.DbangMax, 4)

        self.assertTrue(simops.FEmissionRX)

    def testexport_grainboundaries(self):
        # Create options
        mat1 = Material('Mat1', {79: 0.5, 47: 0.5}, absorption_energy_electron_eV=123)
        mat2 = Material('Mat2', {29: 0.5, 30: 0.5}, absorption_energy_electron_eV=89)
        mat3 = Material('Mat3', {13: 0.5, 14: 0.5}, absorption_energy_electron_eV=89)

        ops = Options()
        ops.beam.energy_eV = 1234
        ops.beam.diameter_m = 25e-9
        ops.beam.origin_m = (100e-9, 0, 1)

        ops.geometry = GrainBoundaries(mat1, mat2)
        ops.geometry.add_layer(mat3, 25e-9)

        ops.limits.add(ShowersLimit(5678))

        # Export to CAS
        casfile = self.e.export(ops)

        # Test
        simdata = casfile.getOptionSimulationData()
        simops = simdata.getSimulationOptions()
        regionops = simdata.getRegionOptions()

        self.assertAlmostEqual(1.234, simops.getIncidentEnergy_keV(0), 4)
        self.assertAlmostEqual(34.93392125, simops.Beam_Diameter, 4) # FWHM
        self.assertAlmostEqual(100.0, simops._positionStart_nm, 4)

        self.assertEqual(3, regionops.getNumberRegions())

        region = regionops.getRegion(0)
        elements = map(attrgetter('Z'), region.getElements())
        self.assertAlmostEqual(mat1.density_kg_m3, region.Rho, 4)
        self.assertEqual('Mat1', region.Name)
        self.assertEqual(2, len(elements))
        self.assertTrue(79 in elements)
        self.assertTrue(47 in elements)

        region = regionops.getRegion(1)
        elements = map(attrgetter('Z'), region.getElements())
        self.assertAlmostEqual(mat3.density_kg_m3, region.Rho, 4)
        self.assertEqual('Mat3', region.Name)
        self.assertEqual(2, len(elements))
        self.assertTrue(13 in elements)
        self.assertTrue(14 in elements)

        region = regionops.getRegion(2)
        elements = map(attrgetter('Z'), region.getElements())
        self.assertAlmostEqual(mat2.density_kg_m3, region.Rho, 4)
        self.assertEqual('Mat2', region.Name)
        self.assertEqual(2, len(elements))
        self.assertTrue(29 in elements)
        self.assertTrue(30 in elements)

        self.assertAlmostEqual(0.089, simops.Eminimum, 3)

        self.assertEqual(5678, simops.getNumberElectrons())

        self.assertFalse(simops.FEmissionRX)

    def testexport_multilayers1(self):
        # Create options
        mat1 = Material('Mat1', {79: 0.5, 47: 0.5}, absorption_energy_electron_eV=123)
        mat2 = Material('Mat2', {29: 0.5, 30: 0.5}, absorption_energy_electron_eV=89)
        mat3 = Material('Mat3', {13: 0.5, 14: 0.5}, absorption_energy_electron_eV=89)

        ops = Options()
        ops.beam.energy_eV = 1234
        ops.beam.diameter_m = 25e-9
        ops.beam.origin_m = (100e-9, 0, 1)

        ops.geometry = MultiLayers(mat1)
        ops.geometry.add_layer(mat2, 25e-9)
        ops.geometry.add_layer(mat3, 55e-9)

        ops.limits.add(ShowersLimit(5678))

        # Export to CAS
        casfile = self.e.export(ops)

        # Test
        simdata = casfile.getOptionSimulationData()
        simops = simdata.getSimulationOptions()
        regionops = simdata.getRegionOptions()

        self.assertAlmostEqual(1.234, simops.getIncidentEnergy_keV(0), 4)
        self.assertAlmostEqual(34.93392125, simops.Beam_Diameter, 4) # FWHM
        self.assertAlmostEqual(100.0, simops._positionStart_nm, 4)

        self.assertEqual(3, regionops.getNumberRegions())

        region = regionops.getRegion(0)
        elements = map(attrgetter('Z'), region.getElements())
        self.assertAlmostEqual(mat2.density_kg_m3, region.Rho, 4)
        self.assertEqual('Mat2', region.Name)
        self.assertEqual(2, len(elements))
        self.assertTrue(29 in elements)
        self.assertTrue(30 in elements)

        region = regionops.getRegion(1)
        elements = map(attrgetter('Z'), region.getElements())
        self.assertAlmostEqual(mat3.density_kg_m3, region.Rho, 4)
        self.assertEqual('Mat3', region.Name)
        self.assertEqual(2, len(elements))
        self.assertTrue(13 in elements)
        self.assertTrue(14 in elements)

        region = regionops.getRegion(2)
        elements = map(attrgetter('Z'), region.getElements())
        self.assertAlmostEqual(mat1.density_kg_m3, region.Rho, 4)
        self.assertEqual('Mat1', region.Name)
        self.assertEqual(2, len(elements))
        self.assertTrue(79 in elements)
        self.assertTrue(47 in elements)

        self.assertAlmostEqual(0.089, simops.Eminimum, 3)

        self.assertEqual(5678, simops.getNumberElectrons())

        self.assertFalse(simops.FEmissionRX)

    def testexport_multilayers2(self):
        # Create options
        mat1 = Material('Mat1', {79: 0.5, 47: 0.5}, absorption_energy_electron_eV=123)
        mat2 = Material('Mat2', {29: 0.5, 30: 0.5}, absorption_energy_electron_eV=89)
        mat3 = Material('Mat3', {13: 0.5, 14: 0.5}, absorption_energy_electron_eV=89)

        ops = Options()
        ops.beam.energy_eV = 1234
        ops.beam.diameter_m = 25e-9
        ops.beam.origin_m = (100e-9, 0, 1)

        ops.geometry = MultiLayers(None)
        ops.geometry.add_layer(mat1, 15e-9)
        ops.geometry.add_layer(mat2, 25e-9)
        ops.geometry.add_layer(mat3, 55e-9)

        ops.limits.add(ShowersLimit(5678))

        # Export to CAS
        casfile = self.e.export(ops)

        # Test
        simdata = casfile.getOptionSimulationData()
        simops = simdata.getSimulationOptions()
        regionops = simdata.getRegionOptions()

        self.assertAlmostEqual(1.234, simops.getIncidentEnergy_keV(0), 4)
        self.assertAlmostEqual(34.93392125, simops.Beam_Diameter, 4) # FWHM
        self.assertAlmostEqual(100.0, simops._positionStart_nm, 4)

        self.assertEqual(3, regionops.getNumberRegions())

        region = regionops.getRegion(0)
        elements = map(attrgetter('Z'), region.getElements())
        self.assertAlmostEqual(mat1.density_kg_m3, region.Rho, 4)
        self.assertEqual('Mat1', region.Name)
        self.assertEqual(2, len(elements))
        self.assertTrue(79 in elements)
        self.assertTrue(47 in elements)

        region = regionops.getRegion(1)
        elements = map(attrgetter('Z'), region.getElements())
        self.assertAlmostEqual(mat2.density_kg_m3, region.Rho, 4)
        self.assertEqual('Mat2', region.Name)
        self.assertEqual(2, len(elements))
        self.assertTrue(29 in elements)
        self.assertTrue(30 in elements)

        region = regionops.getRegion(2)
        elements = map(attrgetter('Z'), region.getElements())
        self.assertAlmostEqual(mat3.density_kg_m3, region.Rho, 4)
        self.assertEqual('Mat3', region.Name)
        self.assertEqual(2, len(elements))
        self.assertTrue(13 in elements)
        self.assertTrue(14 in elements)

        self.assertAlmostEqual(0.089, simops.Eminimum, 3)

        self.assertEqual(5678, simops.getNumberElectrons())

        self.assertFalse(simops.FEmissionRX)

    def testexport_models(self):
        # Create options
        mat = Material('Mat1', {79: 0.5, 47: 0.5}, absorption_energy_electron_eV=123)
        ops = Options()
        ops.beam.energy_eV = 1234
        ops.beam.diameter_m = 25e-9
        ops.beam.origin_m = (100e-9, 0, 1)
        ops.geometry.material = mat
        ops.limits.add(ShowersLimit(5678))

        ops.models.add(ELASTIC_CROSS_SECTION.mott_drouin1993)
        ops.models.add(IONIZATION_CROSS_SECTION.gryzinsky)
        ops.models.add(IONIZATION_POTENTIAL.hovington)
        ops.models.add(RANDOM_NUMBER_GENERATOR.mersenne)
        ops.models.add(DIRECTION_COSINE.soum1979)

        # Export to CAS
        casfile = self.e.export(ops)

        # Test
        simdata = casfile.getOptionSimulationData()
        simops = simdata.getSimulationOptions()

        self.assertAlmostEqual(1.234, simops.getIncidentEnergy_keV(0), 4)
        self.assertAlmostEqual(34.93392125, simops.Beam_Diameter, 4) # FWHM
        self.assertAlmostEqual(100.0, simops._positionStart_nm, 4)

        self.assertEqual(5678, simops.getNumberElectrons())

        self.assertEqual(CROSS_SECTION_MOTT_EQUATION, simops.getTotalElectronElasticCrossSection())
        self.assertEqual(CROSS_SECTION_MOTT_EQUATION, simops.getPartialElectronElasticCrossSection())
        self.assertEqual(IONIZATION_CROSS_SECTION_GRYZINSKI, simops.getIonizationCrossSectionType())
        self.assertEqual(IONIZATION_POTENTIAL_HOVINGTON, simops.getIonizationPotentialType())
        self.assertEqual(DIRECTION_COSINES_SOUM, simops.getDirectionCosines())
        self.assertEqual(ENERGY_LOSS_JOY_LUO, simops.getEnergyLossType())
        self.assertEqual(RANDOM_NUMBER_GENERATOR_MERSENNE_TWISTER, simops.getRandomNumberGeneratorType())

    def testexport_different_openings(self):
        # Create options
        mat = Material('Mat1', {79: 0.5, 47: 0.5}, absorption_energy_electron_eV=123)
        ops = Options()
        ops.beam.energy_eV = 1234
        ops.beam.diameter_m = 25e-9
        ops.beam.origin_m = (100e-9, 0, 1)
        ops.geometry.material = mat
        ops.limits.add(ShowersLimit(5678))
        ops.detectors['xrays'] = \
            PhotonIntensityDetector((radians(30), radians(40)), (0, radians(360.0)))
        ops.detectors['prz'] = \
            PhiRhoZDetector((radians(30), radians(55)), (0, radians(360.0)), 750)

        # Test
        self.assertRaises(ExporterException, self.e.export, ops)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
