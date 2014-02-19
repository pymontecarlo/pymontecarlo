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
from math import radians

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.program.winxray.exporter import Exporter, ExporterException

from pymontecarlo.options.options import Options
from pymontecarlo.options.detector import \
    (BackscatteredElectronEnergyDetector,
     BackscatteredElectronPolarAngularDetector, PhotonIntensityDetector,
     PhotonDepthDetector, PhotonSpectrumDetector)
from pymontecarlo.options.limit import ShowersLimit
from pymontecarlo.options.material import Material
from pymontecarlo.options.particle import ELECTRON
from pymontecarlo.options.model import \
    (ELASTIC_CROSS_SECTION, IONIZATION_CROSS_SECTION, IONIZATION_POTENTIAL,
     RANDOM_NUMBER_GENERATOR, DIRECTION_COSINE, MASS_ABSORPTION_COEFFICIENT)

# Globals and constants variables.
import winxraytools.configuration.DirectionCosine as DirectionCosine
import winxraytools.configuration.EnergyLoss as EnergyLoss
import winxraytools.configuration.EvPerChannel as EvPerChannel
import winxraytools.configuration.ElectronElasticCrossSection as ElectronElasticCrossSection
import winxraytools.configuration.IonizationCrossSection as IonizationCrossSection
import winxraytools.configuration.IonizationPotential as IonizationPotential
import winxraytools.configuration.MassAbsorptionCoefficient as MassAbsorptionCoefficient
import winxraytools.configuration.RandomNumberGenerator as RandomNumberGenerator

class TestExporter(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.e = Exporter()

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testexport_substrate(self):
        # Create options
        mat = Material({79: 0.5, 47: 0.5}, 'Mat1',
                       absorption_energy_eV={ELECTRON: 123.0})

        ops = Options()
        ops.beam.energy_eV = 1234
        ops.beam.diameter_m = 25e-9
        ops.beam.origin_m = (100e-9, 0, 1)
        ops.geometry.body.material = mat
        ops.limits.add(ShowersLimit(5678))
        ops.detectors['bse'] = BackscatteredElectronEnergyDetector(123, (0, 567))
        ops.detectors['bse polar'] = BackscatteredElectronPolarAngularDetector(125)
        ops.detectors['xrays'] = \
            PhotonIntensityDetector((radians(30), radians(40)), (0, radians(360.0)))
        ops.detectors['prz'] = \
            PhotonDepthDetector((radians(30), radians(40)), (0, radians(360.0)), 750)

        # Export to WinX-Ray options
        wxrops = self.e.export_wxroptions(ops)

        # Test
        self.assertAlmostEqual(1.234, wxrops.getIncidentEnergy_keV(), 4)
        self.assertAlmostEqual(25.0, wxrops.getBeamDiameter_nm(), 4)
        self.assertEqual(5678, wxrops.getNbElectron())

        zs, _wfs = wxrops.getElements()
        self.assertTrue(79 in zs)
        self.assertTrue(47 in zs)
        self.assertAlmostEqual(13.6007, wxrops.getMeanDensity_g_cm3(), 4) # internally calculated by WinXray
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
        mat = Material({79: 0.5, 47: 0.5}, 'Mat1',
                       absorption_energy_eV={ELECTRON: 123.0})

        ops = Options()
        ops.beam.energy_eV = 1234
        ops.beam.diameter_m = 25e-9
        ops.geometry.body.material = mat
        ops.limits.add(ShowersLimit(5678))
        ops.detectors['spectrum'] = \
            PhotonSpectrumDetector((radians(30), radians(40)), (0, radians(360.0)),
                                   500, (0, 1234))

        # Export to WinX-Ray options
        wxrops = self.e.export_wxroptions(ops)

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
        mat = Material({79: 0.5, 47: 0.5}, 'Mat1',
                       absorption_energy_eV={ELECTRON: 123.0})

        ops = Options()
        ops.beam.energy_eV = 1234
        ops.beam.diameter_m = 25e-9
        ops.geometry.body.material = mat
        ops.limits.add(ShowersLimit(5678))

        ops.models.add(ELASTIC_CROSS_SECTION.rutherford)
        ops.models.add(IONIZATION_CROSS_SECTION.casnati1982)
        ops.models.add(IONIZATION_POTENTIAL.joy_luo1989)
        ops.models.add(RANDOM_NUMBER_GENERATOR.press1966_rand3)
        ops.models.add(DIRECTION_COSINE.demers2000)
        ops.models.add(MASS_ABSORPTION_COEFFICIENT.thinh_leroux1979)

        # Export to WinX-Ray options
        wxrops = self.e.export_wxroptions(ops)

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

    def testexport_different_opening(self):
        # Create options
        mat = Material({79: 0.5, 47: 0.5}, 'Mat1',
                       absorption_energy_eV={ELECTRON: 123.0})

        ops = Options()
        ops.beam.energy_eV = 1234
        ops.beam.diameter_m = 25e-9
        ops.geometry.body.material = mat
        ops.limits.add(ShowersLimit(5678))
        ops.detectors['xrays'] = \
            PhotonIntensityDetector((radians(30), radians(40)), (0, radians(360.0)))
        ops.detectors['prz'] = \
            PhotonDepthDetector((radians(30), radians(50)), (0, radians(360.0)), 750)

        # Test
        self.assertRaises(ExporterException, self.e.export_wxroptions, ops)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
