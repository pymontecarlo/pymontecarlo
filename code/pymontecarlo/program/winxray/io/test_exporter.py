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
import warnings
from math import radians

# Third party modules.

# Local modules.
from pymontecarlo.program.winxray.io.exporter import Exporter

from pymontecarlo.input.options import Options
from pymontecarlo.input.detector import \
    (BackscatteredElectronEnergyDetector,
     BackscatteredElectronPolarAngularDetector, PhotonIntensityDetector,
     PhiRhoZDetector, PhotonSpectrumDetector)
from pymontecarlo.input.limit import ShowersLimit
from pymontecarlo.input.material import Material
from pymontecarlo.input.model import \
    (ELASTIC_CROSS_SECTION, IONIZATION_CROSS_SECTION, IONIZATION_POTENTIAL,
     RANDOM_NUMBER_GENERATOR, DIRECTION_COSINE, MASS_ABSORPTION_COEFFICIENT)

# Globals and constants variables.
import winxrayTools.Configuration.DirectionCosine as DirectionCosine
import winxrayTools.Configuration.EnergyLoss as EnergyLoss
import winxrayTools.Configuration.EvPerChannel as EvPerChannel
import winxrayTools.Configuration.ElectronElasticCrossSection as ElectronElasticCrossSection
import winxrayTools.Configuration.IonizationCrossSection as IonizationCrossSection
import winxrayTools.Configuration.IonizationPotential as IonizationPotential
import winxrayTools.Configuration.MassAbsorptionCoefficient as MassAbsorptionCoefficient
import winxrayTools.Configuration.RandomNumberGenerator as RandomNumberGenerator

warnings.simplefilter("always")

class TestExporter(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.e = Exporter()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

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
        ops.detectors['bse polar'] = BackscatteredElectronPolarAngularDetector(125)
        ops.detectors['xrays'] = \
            PhotonIntensityDetector((radians(30), radians(40)), (0, radians(360.0)))
        ops.detectors['prz'] = \
            PhiRhoZDetector((radians(30), radians(40)), (0, radians(360.0)),
                            (-12.34, -56.78), 750)

        # Export to WinX-Ray options
        with warnings.catch_warnings(record=True) as ws:
            wxrops = self.e.export(ops)

        # 1 warning for beam origin
        self.assertEqual(1, len(ws))

        # Test
        self.assertAlmostEqual(1.234, wxrops.getIncidentEnergy_keV(), 4)
        self.assertAlmostEqual(25.0, wxrops.getBeamDiameter_nm(), 4)
        self.assertEqual(5678, wxrops.getNbElectron())

        zs, _wfs = wxrops.getElements()
        self.assertTrue(79 in zs)
        self.assertTrue(47 in zs)
        self.assertAlmostEqual(mat.density_kg_m3, wxrops.getMeanDensity_g_cm3(), 4)
        self.assertAlmostEqual(123, wxrops.getMinimumElectronEnergy_eV(), 4)

        self.assertTrue(wxrops.isComputeBSEDistribution())
        self.assertTrue(wxrops.isComputeBSEEnergy())
        self.assertEqual(123, wxrops.getNbBSEEnergy())
        self.assertTrue(wxrops.isComputeBSEAngular())
        self.assertEqual(125, wxrops.getNbBSEAngular())

        self.assertTrue(wxrops.isXrayCompute())
        self.assertTrue(wxrops.isXrayComputeCharacteristic())
        self.assertAlmostEqual(35.0, wxrops.getTOA_deg(), 4)
        self.assertAlmostEqual(55, wxrops.getAngleThetaDetector_deg(), 4)
        self.assertAlmostEqual(180.0, wxrops.getAnglePhiDetector_deg(), 4)
        self.assertEqual(750, wxrops.getNumberFilm())

    def testexport_spectrum(self):
        # Create options
        mat = Material('Mat1', {79: 0.5, 47: 0.5}, absorption_energy_electron_eV=123)
        ops = Options()
        ops.beam.energy_eV = 1234
        ops.beam.diameter_m = 25e-9
        ops.geometry.material = mat
        ops.limits.add(ShowersLimit(5678))
        ops.detectors['spectrum'] = \
            PhotonSpectrumDetector((radians(30), radians(40)), (0, radians(360.0)),
                                   (0, 1234), 500)

        # Export to WinX-Ray options
        wxrops = self.e.export(ops)

        # Test
        self.assertTrue(wxrops.isXrayCompute())
        self.assertTrue(wxrops.isXrayComputeCharacteristic())
        self.assertAlmostEqual(35.0, wxrops.getTOA_deg(), 4)
        self.assertAlmostEqual(55, wxrops.getAngleThetaDetector_deg(), 4)
        self.assertAlmostEqual(180.0, wxrops.getAnglePhiDetector_deg(), 4)
        self.assertEqual(EvPerChannel.TYPE_5, wxrops.getTypeEVChannel())
        self.assertEqual(246, wxrops.getNumberChannel())

    def testexport_models(self):
        # Create options
        mat = Material('Mat1', {79: 0.5, 47: 0.5}, absorption_energy_electron_eV=123)
        ops = Options()
        ops.beam.energy_eV = 1234
        ops.beam.diameter_m = 25e-9
        ops.geometry.material = mat
        ops.limits.add(ShowersLimit(5678))

        ops.models.add(ELASTIC_CROSS_SECTION.rutherford)
        ops.models.add(IONIZATION_CROSS_SECTION.casnati1982)
        ops.models.add(IONIZATION_POTENTIAL.joy_luo1989)
        ops.models.add(RANDOM_NUMBER_GENERATOR.press1966_rand3)
        ops.models.add(DIRECTION_COSINE.demers2000)
        ops.models.add(MASS_ABSORPTION_COEFFICIENT.thinh_leroux1979)

        # Export to WinX-Ray options
        wxrops = self.e.export(ops)

        # Test
        self.assertEqual(ElectronElasticCrossSection.TYPE_RUTHERFORD, wxrops.getTypePartialCrossSection())
        self.assertEqual(ElectronElasticCrossSection.TYPE_RUTHERFORD, wxrops.getTypeTotalCrossSection())
        self.assertEqual(IonizationCrossSection.TYPE_CASNATI, wxrops.getTypeXrayCrossSectionBremsstrahlung())
        self.assertEqual(IonizationCrossSection.TYPE_CASNATI, wxrops.getTypeXrayCrossSectionCharacteristic())
        self.assertEqual(IonizationPotential.TYPE_JOY_LUO, wxrops.getTypeIonisationPotential())
        self.assertEqual(DirectionCosine.TYPE_DEMERS, wxrops.getTypeDirectionCosines())
        self.assertEqual(EnergyLoss.TYPE_JOY_LUO, wxrops.getTypeEnergyLoss())
        self.assertEqual(RandomNumberGenerator.TYPE_RAN3, wxrops.getTypeRandomGenerator())
        self.assertEqual(MassAbsorptionCoefficient.TYPE_THINH_LEROUX, wxrops.getTypeMac())


if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
