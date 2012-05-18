#!/usr/bin/env python
"""
================================================================================
:mod:`exporter` -- Exporter to WXC
================================================================================

.. module:: exporter
   :synopsis: Exporter to WXC

.. inheritance-diagram:: pymontecarlo.program.winxray.io.exporter

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import math
import warnings
from operator import attrgetter, itemgetter

# Third party modules.

# Local modules.
from pymontecarlo.input.beam import GaussianBeam
from pymontecarlo.input.geometry import Substrate
from pymontecarlo.input.limit import ShowersLimit
from pymontecarlo.input.detector import \
    (_DelimitedDetector,
     BackscatteredElectronEnergyDetector,
     BackscatteredElectronPolarAngularDetector,
     PhiRhoZDetector,
     PhotonIntensityDetector,
     PhotonSpectrumDetector,
     ElectronFractionDetector,
     TimeDetector
     )
from pymontecarlo.input.model import \
    (ELASTIC_CROSS_SECTION, IONIZATION_CROSS_SECTION, IONIZATION_POTENTIAL,
     RANDOM_NUMBER_GENERATOR, DIRECTION_COSINE, ENERGY_LOSS, MASS_ABSORPTION_COEFFICIENT)
from pymontecarlo.io.exporter import Exporter as _Exporter, ExporterWarning

from winxrayTools.Configuration.OptionsFile import OptionsFile

# Globals and constants variables.
#import winxrayTools.Configuration.Crystal as Crystal
import winxrayTools.Configuration.DirectionCosine as DirectionCosine
import winxrayTools.Configuration.EnergyLoss as EnergyLoss
import winxrayTools.Configuration.EvPerChannel as EvPerChannel
import winxrayTools.Configuration.ElectronElasticCrossSection as ElectronElasticCrossSection
import winxrayTools.Configuration.IonizationCrossSection as IonizationCrossSection
import winxrayTools.Configuration.IonizationPotential as IonizationPotential
import winxrayTools.Configuration.MassAbsorptionCoefficient as MassAbsorptionCoefficient
import winxrayTools.Configuration.RandomNumberGenerator as RandomNumberGenerator
#import winxrayTools.Configuration.Window as Window

class Exporter(_Exporter):

    def __init__(self):
        _Exporter.__init__(self)

        self._beam_exporters[GaussianBeam] = self._beam_gaussian

        self._geometry_exporters[Substrate] = self._geometry_substrate

        self._detector_exporters[BackscatteredElectronEnergyDetector] = \
            self._detector_backscattered_electron_energy
        self._detector_exporters[BackscatteredElectronPolarAngularDetector] = \
            self._detector_backscattered_electron_polar_angular
        self._detector_exporters[PhiRhoZDetector] = \
            self._detector_phirhoz
        self._detector_exporters[PhotonIntensityDetector] = \
            self._detector_photon_intensity
        self._detector_exporters[PhotonSpectrumDetector] = \
            self._detector_photon_spectrum
        self._detector_exporters[ElectronFractionDetector] = \
            self._detector_electron_fraction
        self._detector_exporters[TimeDetector] = \
            self._detector_time

        self._limit_exporters[ShowersLimit] = self._limit_showers

        self._model_exporters[ELASTIC_CROSS_SECTION.type] = \
            self._model_elastic_cross_section
        self._model_exporters[IONIZATION_CROSS_SECTION.type] = \
            self._model_ionization_cross_section
        self._model_exporters[IONIZATION_POTENTIAL.type] = \
            self._model_ionization_potential
        self._model_exporters[RANDOM_NUMBER_GENERATOR.type] = \
            self._model_random_number_generator
        self._model_exporters[DIRECTION_COSINE.type] = \
            self._model_direction_cosine
        self._model_exporters[ENERGY_LOSS.type] = \
            self._model_energy_loss
        self._model_exporters[MASS_ABSORPTION_COEFFICIENT.type] = \
            self._model_mass_absorption_coefficient

    def export(self, options):
        """
        Exports options to WinX-Ray options.
        
        :rtype: :class:`OptionsFile <winxrayTools.Configuration.OptionsFile.OptionsFile>`
        """
        wxrops = OptionsFile()

        # Default options
        wxrops.setSaveFile(True) # Save results to file

        self._export(options, wxrops)

        return wxrops

    def _export_detectors(self, options, wxrops):
        # Deactivate all detectors
        wxrops.setXrayCompute(False)
        wxrops.setXrayComputeBackground(False)
        wxrops.setXrayComputeCharacteristic(False)

        wxrops.setComputeBSEDistribution(False)
        wxrops.setComputeBSEDepth(False)
        wxrops.setComputeBSERadial(False)
        wxrops.setComputeBSESpatial(False)
        wxrops.setComputeBSELateral(False)
        wxrops.setComputeBSEEnergy(False)
        wxrops.setComputeBSEAngular(False)

        wxrops.setComputeSEDistribution(False)

        wxrops.setComputeEnergyLossDistribution(False)
        wxrops.setComputeEnergyLossDepth(False)
        wxrops.setComputeEnergyLossLateral(False)
        wxrops.setComputeEnergyLossSpatial(False)
        wxrops.setComputeEnergyLossRadial(False)

        wxrops.setComputeElectronDistribution(False)
        wxrops.setComputeElectronDepth(False)
        wxrops.setComputeElectronRadial(False)
        wxrops.setComputeElectronSpatial(False)
        wxrops.setComputeElectronLateral(False)

        # Perform detector export
        _Exporter._export_detectors(self, options, wxrops)

        # Detector position
        dets = options.detectors.findall(_DelimitedDetector).values()
        if dets:
            toa_deg = math.degrees(dets[0].takeoffangle_rad) # deg
            phi_deg = math.degrees(sum(dets[0].azimuth_rad) / 2.0) # deg

            wxrops.setTOA_deg(toa_deg)
            wxrops.setAngleThetaDetector_deg(90.0 - toa_deg)
            wxrops.setAnglePhiDetector_deg(phi_deg)

            wxrops.setUserDefineSolidAngle(True)
            wxrops.setSolidAngle_sr(dets[0].solidangle_sr)

    def _beam_gaussian(self, options, beam, wxrops):
        energy_keV = beam.energy_eV / 1000.0 # keV
        wxrops.setMultiEnergy(False)
        wxrops.setIncidentEnergy_keV(energy_keV)
        wxrops.setStartEnergy_keV(energy_keV)
        wxrops.setEndEnergy_keV(energy_keV)
        wxrops.setStepEnergy_keV(1)
        wxrops.setNbStepEnergy(1)

        wxrops.setBeamDiameter_nm(beam.diameter_m * 1e9) # nm

        if beam.origin_m != (0, 0, 0):
            warnings.warn('No beam position in WinX-Ray', ExporterWarning)

        # TODO: Set beam direction in WinX-Ray exporter
        #wxrops.setBeamPhi_deg
        #wxrops.setBeamTheta_deg

    def _geometry_substrate(self, options, geometry, wxrops):
        material = geometry.material

        composition = material.composition.items()
        zs = map(itemgetter(0), composition)
        wfs = map(itemgetter(1), composition)

        wxrops.setElements(zs, wfs)

        if material.has_density_defined():
            warnings.warn('WinXRay does not support user defined density', ExporterWarning)
        #wxrops.setMeanDensity_g_cm3(material.density_kg_m3)

        # Absorption energy electron
        abs_electron_eV = min(map(attrgetter('absorption_energy_electron_eV'),
                               options.geometry.get_materials()))
        wxrops.setMinimumElectronEnergy_eV(abs_electron_eV)

    def _detector_backscattered_electron_energy(self, options, name,
                                                detector, wxrops):
        wxrops.setComputeBSEDistribution(True)
        wxrops.setComputeBSEEnergy(True)
        wxrops.setNbBSEEnergy(detector.channels)

    def _detector_backscattered_electron_polar_angular(self, options, name,
                                                       detector, wxrops):
        wxrops.setComputeBSEDistribution(True)
        wxrops.setComputeBSEAngular(True)
        wxrops.setNbBSEAngular(detector.channels)

    def _detector_phirhoz(self, options, name, detector, wxrops):
        wxrops.setXrayCompute(True)
        wxrops.setXrayComputeCharacteristic(True)
        wxrops.setNumberFilm(detector.channels)

    def _detector_photon_intensity(self, options, name, detector, wxrops):
        wxrops.setXrayCompute(True)
        wxrops.setXrayComputeCharacteristic(True)

    def _detector_photon_spectrum(self, options, name, detector, wxrops):
        wxrops.setXrayCompute(True)
        wxrops.setXrayComputeBackground(True)
        wxrops.setXrayComputeCharacteristic(True)

        # Channel energy per channel
        ev_per_channel = options.beam.energy_eV / detector.channels
        if ev_per_channel < 10:
            wxrops.setTypeEVChannel(EvPerChannel.TYPE_5)
            wxrops.setNumberChannel(options.beam.energy_eV / 5)
        elif ev_per_channel < 20:
            wxrops.setTypeEVChannel(EvPerChannel.TYPE_10)
            wxrops.setNumberChannel(options.beam.energy_eV / 10)
        elif ev_per_channel < 40:
            wxrops.setTypeEVChannel(EvPerChannel.TYPE_20)
            wxrops.setNumberChannel(options.beam.energy_eV / 20)
        else:
            wxrops.setTypeEVChannel(EvPerChannel.TYPE_40)
            wxrops.setNumberChannel(options.beam.energy_eV / 40)

    def _detector_electron_fraction(self, options, name, detector, wxrops):
        wxrops.setComputeBSEDistribution(True) # Required to get distribution
        wxrops.setComputeBSEEnergy(True) # Required to get distribution

    def _detector_time(self, options, name, detector, wxrops):
        pass

    def _limit_showers(self, options, limit, wxrops):
        wxrops.setNbElectron(limit.showers)

    def _model_elastic_cross_section(self, options, model, wxrops):
        types = {ELASTIC_CROSS_SECTION.mott_czyzewski1990: ElectronElasticCrossSection.TYPE_MOTTTABULATED,
                 ELASTIC_CROSS_SECTION.mott_czyzewski1990_linear: ElectronElasticCrossSection.TYPE_MOTTTABULATEDLINEAR,
                 ELASTIC_CROSS_SECTION.mott_czyzewski1990_powerlaw: ElectronElasticCrossSection.TYPE_MOTTTABULATEDPOWERLAW,
                 ELASTIC_CROSS_SECTION.mott_czyzewski1990_cubicspline: ElectronElasticCrossSection.TYPE_MOTTTABULATEDCUBICSPLINE,
                 ELASTIC_CROSS_SECTION.mott_demers: ElectronElasticCrossSection.TYPE_MOTTPARAMETRIZEDHD,
                 ELASTIC_CROSS_SECTION.rutherford: ElectronElasticCrossSection.TYPE_RUTHERFORD,
                 ELASTIC_CROSS_SECTION.rutherford_relativistic: ElectronElasticCrossSection.TYPE_RUTHERFORDRELATIVISTIC}
        wxrops.setTypeElectronElasticCrossSection(types[model])

    def _model_ionization_cross_section(self, options, model, wxrops):
        types = {IONIZATION_CROSS_SECTION.casnati1982: IonizationCrossSection.TYPE_CASNATI}
        wxrops.setTypeIonizationCrossSection(types[model])

    def _model_ionization_potential(self, options, model, wxrops):
        types = {IONIZATION_POTENTIAL.joy_luo1989: IonizationPotential.TYPE_JOY_LUO}
        wxrops.setTypeIonisationPotential(types[model])

    def _model_random_number_generator(self, options, model, wxrops):
        types = {RANDOM_NUMBER_GENERATOR.press1966_rand1: RandomNumberGenerator.TYPE_RAN1,
                 RANDOM_NUMBER_GENERATOR.press1966_rand2: RandomNumberGenerator.TYPE_RAN2,
                 RANDOM_NUMBER_GENERATOR.press1966_rand3: RandomNumberGenerator.TYPE_RAN3,
                 RANDOM_NUMBER_GENERATOR.press1966_rand4: RandomNumberGenerator.TYPE_RAN4}
        wxrops.setTypeRandomGenerator(types[model])

    def _model_direction_cosine(self, options, model, wxrops):
        types = {DIRECTION_COSINE.demers2000: DirectionCosine.TYPE_DEMERS}
        wxrops.setTypeDirectionCosines(types[model])

    def _model_energy_loss(self, options, model, wxrops):
        types = {ENERGY_LOSS.joy_luo1989: EnergyLoss.TYPE_JOY_LUO}
        wxrops.setTypeEnergyLoss(types[model])

    def _model_mass_absorption_coefficient(self, options, model, wxrops):
        types = {MASS_ABSORPTION_COEFFICIENT.heinrich_ixcom11: MassAbsorptionCoefficient.TYPE_HEINRICH,
                 MASS_ABSORPTION_COEFFICIENT.henke1993: MassAbsorptionCoefficient.TYPE_HENKE,
                 MASS_ABSORPTION_COEFFICIENT.thinh_leroux1979: MassAbsorptionCoefficient.TYPE_THINH_LEROUX}
        wxrops.setTypeMac(types[model])


