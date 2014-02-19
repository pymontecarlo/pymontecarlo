#!/usr/bin/env python
"""
================================================================================
:mod:`exporter` -- Exporter to CAS file
================================================================================

.. module:: exporter
   :synopsis: Exporter to CAS file

.. inheritance-diagram:: pymontecarlo.program.casino2.input.exporter

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
from operator import itemgetter
import warnings

# Third party modules.
import numpy as np
import pyxray.element_properties as ep
from pkg_resources import resource_stream #@UnresolvedImport

# Local modules.
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.particle import ELECTRON
from pymontecarlo.options.geometry import  \
    Substrate, HorizontalLayers, VerticalLayers
from pymontecarlo.options.limit import ShowersLimit
from pymontecarlo.options.detector import \
    (_DelimitedDetector,
     BackscatteredElectronEnergyDetector,
     BackscatteredElectronPolarAngularDetector,
     BackscatteredElectronRadialDetector,
     PhotonDepthDetector,
     PhotonRadialDetector,
     PhotonIntensityDetector,
     TransmittedElectronEnergyDetector,
     ElectronFractionDetector,
     equivalent_opening,
     TrajectoryDetector,
     )
from pymontecarlo.options.model import \
    (ELASTIC_CROSS_SECTION, IONIZATION_CROSS_SECTION, IONIZATION_POTENTIAL,
     RANDOM_NUMBER_GENERATOR, DIRECTION_COSINE, ENERGY_LOSS, MASS_ABSORPTION_COEFFICIENT)
from pymontecarlo.program.exporter import \
    Exporter as _Exporter, ExporterException, ExporterWarning

from casinotools.fileformat.casino2.File import File
from casinotools.fileformat.casino2.SimulationOptions import \
    (DIRECTION_COSINES_SOUM, DIRECTION_COSINES_DROUIN,
     CROSS_SECTION_MOTT_JOY, CROSS_SECTION_MOTT_EQUATION,
     CROSS_SECTION_MOTT_BROWNING, CROSS_SECTION_MOTT_RUTHERFORD,
     IONIZATION_CROSS_SECTION_GAUVIN, IONIZATION_CROSS_SECTION_POUCHOU,
     IONIZATION_CROSS_SECTION_BROWN_POWELL, IONIZATION_CROSS_SECTION_CASNATI,
     IONIZATION_CROSS_SECTION_GRYZINSKI, IONIZATION_CROSS_SECTION_JAKOBY,
     IONIZATION_POTENTIAL_JOY, IONIZATION_POTENTIAL_BERGER,
     IONIZATION_POTENTIAL_HOVINGTON,
     RANDOM_NUMBER_GENERATOR_PRESS_ET_AL, RANDOM_NUMBER_GENERATOR_MERSENNE_TWISTER,
     ENERGY_LOSS_JOY_LUO)

# Globals and constants variables.

def _setup_region_material(region, material):
    region.removeAllElements()

    for z, fraction in material.composition.items():
        region.addElement(ep.symbol(z), weightFraction=fraction)

    region.update() # Calculate number of elements, mean atomic number

    region.User_Density = True
    region.Rho = material.density_kg_m3 / 1000.0 # g/cm3
    region.Name = material.name

class Exporter(_Exporter):

    def __init__(self):
        _Exporter.__init__(self)

        self._beam_exporters[GaussianBeam] = self._beam_gaussian

        self._geometry_exporters[Substrate] = self._geometry_substrate
        self._geometry_exporters[HorizontalLayers] = self._geometry_horizontal_layers
        self._geometry_exporters[VerticalLayers] = self._geometry_vertical_layers

        self._detector_exporters[BackscatteredElectronEnergyDetector] = \
            self._detector_backscattered_electron_energy
        self._detector_exporters[BackscatteredElectronPolarAngularDetector] = \
            self._detector_backscattered_electron_polar_angular
        self._detector_exporters[BackscatteredElectronRadialDetector] = \
            self._detector_backscattered_electron_radial
        self._detector_exporters[TransmittedElectronEnergyDetector] = \
            self._detector_transmitted_electron_energy
        self._detector_exporters[PhotonDepthDetector] = \
            self._detector_photondepth
        self._detector_exporters[PhotonRadialDetector] = \
            self._detector_photonradial
        self._detector_exporters[PhotonIntensityDetector] = \
            self._detector_photon_intensity
        self._detector_exporters[ElectronFractionDetector] = \
            self._detector_electron_fraction
        self._detector_exporters[TrajectoryDetector] = \
            self._detector_trajectory

        self._limit_exporters[ShowersLimit] = self._limit_showers

        self._model_exporters[ELASTIC_CROSS_SECTION] = \
            self._model_elastic_cross_section
        self._model_exporters[IONIZATION_CROSS_SECTION] = \
            self._model_ionization_cross_section
        self._model_exporters[IONIZATION_POTENTIAL] = \
            self._model_ionization_potential
        self._model_exporters[RANDOM_NUMBER_GENERATOR] = \
            self._model_random_number_generator
        self._model_exporters[DIRECTION_COSINE] = \
            self._model_direction_cosine
        self._model_exporters[ENERGY_LOSS] = \
            self._model_energy_loss
        self._model_exporters[MASS_ABSORPTION_COEFFICIENT] = \
            self._model_mass_absorption_coefficient

    def _export(self, options, dirpath, *args, **kwargs):
        casfile = self.export_cas(options)

        filepath = os.path.join(dirpath, options.name + '.sim')
        casfile.write(filepath)

        return filepath

    def export_cas(self, options):
        casfile = File()

        # Load template (from geometry)
        fileobj = self._get_sim_template(options)
        casfile.readFromFileObject(fileobj)

        simdata = casfile.getOptionSimulationData()
        simops = simdata.getSimulationOptions()

        self._run_exporters(options, simdata, simops)

        return casfile

    def _get_sim_template(self, options):
        geometry = options.geometry
        geometry_name = geometry.__class__.__name__

        if isinstance(geometry, Substrate):
            return resource_stream(__name__, "templates/Substrate.sim")
        elif isinstance(geometry, (HorizontalLayers, VerticalLayers)):
            regions_count = len(np.array(geometry.layers, ndmin=1))

            if isinstance(geometry, HorizontalLayers):
                if geometry.has_substrate(): regions_count += 1
            else: # GrainBoundaries
                regions_count += 2 # left and right regions

            filename = "%s%i.sim" % (geometry_name, regions_count)
            buffer = resource_stream(__name__, "templates/" + filename)
            if buffer is None:
                raise ExporterException("No template for '%s' with region count: %i" % \
                                        (geometry_name, regions_count))
            return buffer
        else:
            raise ExporterException("Unknown geometry: %s" % geometry_name)

    def _beam_gaussian(self, options, beam, simdata, simops):
        simops.setIncidentEnergy_keV(beam.energy_eV / 1000.0) # keV
        simops.setPosition(beam.origin_m[0] * 1e9) # nm

        # Beam diameter
        # Casino's beam diameter contains 99.9% of the electrons (n=3.290)
        # d_{CASINO} = 2 (3.2905267 \sigma)
        # d_{FWHM} = 2 (1.177411 \sigma)
        # d_{CASINO} = 2.7947137 d_{FWHM}
        # NOTE: The attribute Beam_Diameter corresponds in fact to the beam
        # radius.
        simops.Beam_Diameter = 2.7947137 * beam.diameter_m * 1e9 / 2.0 # nm

        # Beam tilt
        simops.Beam_angle = np.degrees(beam.direction_polar_rad)

    def _export_geometry(self, options, simdata, simops):
        _Exporter._export_geometry(self, options, simdata, simops)

        if options.geometry.tilt_rad != 0.0:
            message = 'Casino does not support sample tilt. Use beam tilt instead.'
            warnings.warn(message, ExporterWarning)

        if options.geometry.rotation_rad != 0.0:
            message = 'Casino does not support sample rotation.'
            warnings.warn(message, ExporterWarning)

        # Absorption energy electron
        abs_electron_eV = min(mat.absorption_energy_eV[ELECTRON] \
                              for mat in options.geometry.get_materials())
        simops.Eminimum = abs_electron_eV / 1000.0 # keV

    def _geometry_substrate(self, options, geometry, simdata, simops):
        regionops = simdata.getRegionOptions()

        region = regionops.getRegion(0)
        _setup_region_material(region, geometry.body.material)

    def _geometry_horizontal_layers(self, options, geometry, simdata, simops):
        regionops = simdata.getRegionOptions()
        layers = geometry.layers

        for i, layer in enumerate(layers):
            region = regionops.getRegion(i)
            _setup_region_material(region, layer.material)

            parameters = [abs(layer.zmax_m) * 1e9, abs(layer.zmin_m) * 1e9, 0.0, 0.0]
            region.setParameters(parameters)

        if geometry.has_substrate():
            region = regionops.getRegion(regionops.getNumberRegions() - 1)
            _setup_region_material(region, geometry.substrate.material)

            parameters = region.getParameters()
            parameters[0] = abs(geometry.substrate.zmax_m) * 1e9
            parameters[2] = parameters[0] + 10.0
            region.setParameters(parameters)

    def _geometry_vertical_layers(self, options, geometry, simdata, simops):
        regionops = simdata.getRegionOptions()
        layers = np.array(geometry.layers, ndmin=1)
        assert len(layers) == regionops.getNumberRegions() - 2 # without substrates

        # Left substrate
        region = regionops.getRegion(0)
        _setup_region_material(region, geometry.left_substrate.material)

        parameters = region.getParameters()
        parameters[1] = geometry.left_substrate.xmax_m * 1e9
        parameters[2] = parameters[1] - 10.0
        region.setParameters(parameters)

        # Layers
        for i, layer in enumerate(layers):
            region = regionops.getRegion(i + 1)
            _setup_region_material(region, layer.material)

            parameters = [layer.xmin_m * 1e9, layer.xmax_m * 1e9, 0.0, 0.0]
            region.setParameters(parameters)

        # Right substrate
        region = regionops.getRegion(regionops.getNumberRegions() - 1)
        _setup_region_material(region, geometry.right_substrate.material)

        parameters = region.getParameters()
        parameters[0] = geometry.right_substrate.xmin_m * 1e9
        parameters[2] = parameters[0] + 10.0
        region.setParameters(parameters)

    def _export_detectors(self, options, simdata, simops):
        simops.RangeFinder = 3 # Fixed range
        simops.FEmissionRX = 0 # Do not simulate x-rays
        simops.Memory_Keep = 0 # Do not save trajectories

        _Exporter._export_detectors(self, options, simdata, simops)

        # Detector position
        dets = options.detectors.iterclass(_DelimitedDetector)
        dets = list(map(itemgetter(1), dets))

        if len(dets) >= 2:
            c = map(equivalent_opening, dets[:-1], dets[1:])
            if not all(c):
                raise ExporterException("Some delimited detectors do not have the same opening")

        if dets:
            simops.TOA = np.degrees(dets[0].takeoffangle_rad) # deg
            simops.PhieRX = np.degrees(sum(dets[0].azimuth_rad) / 2.0) # deg

    def _detector_backscattered_electron_energy(self, options, name,
                                                detector, simdata, simops):
        simops.FDenr = 1
        simops.FDenrLog = 0
        simops.NbPointDENR = detector.channels
        simops.DenrMin = detector.limits_eV[0] / 1000.0 # keV
        simops.DenrMax = detector.limits_eV[1] / 1000.0 # keV

    def _detector_transmitted_electron_energy(self, options, name,
                                              detector, simdata, simops):
        simops.FDent = 1
        simops.FDentLog = 0
        simops.NbPointDENT = detector.channels
        simops.DentMin = detector.limits_eV[0] / 1000.0 # keV
        simops.DentMax = detector.limits_eV[1] / 1000.0 # keV

    def _detector_backscattered_electron_polar_angular(self, options, name,
                                                       detector, simdata, simops):
        simops.FDbang = 1
        simops.FDbangLog = 0
        simops.NbPointDBANG = detector.channels
        simops.DbangMin = np.degrees(detector.limits_rad[0]) # deg
        simops.DbangMax = np.degrees(detector.limits_rad[1]) # deg

    def _detector_backscattered_electron_radial(self, options, name,
                                                detector, simdata, simops):
        simops.FDrsr = 1
        simops.FDrsrLog = 0
        simops.NbPointDRSR = detector.channels
#        simops.DrsrMax =
#        simops.DrsrMin =

    def _detector_photondepth(self, options, name, detector, simdata, simops):
        # FIXME: Casino freezes when this value is set
        #simops.NbreCoucheRX = detector.channels
        simops.FEmissionRX = 1 # Simulate x-ray

    def _detector_photonradial(self, options, name, detector, simdata, simops):
        simops.FEmissionRX = 1 # Simulate x-rays
        # FIXME: Simulation options parameters for the number of channels radially

    def _detector_photon_intensity(self, options, name, detector, simdata, simops):
        simops.FEmissionRX = 1 # Simulate x-rays

    def _detector_electron_fraction(self, options, name, detector, simdata, simops):
        pass

    def _detector_trajectory(self, options, name, detector, simdata, simops):
        simops.Memory_Keep = 1
        limit = list(options.limits.iterclass(ShowersLimit))[0]
        simops.Electron_Display = limit.showers
#        simops.Electron_Save = 5 # Save interval (min)

    def _limit_showers(self, options, limit, simdata, simops):
        simops.setNumberElectrons(limit.showers)

    def _model_elastic_cross_section(self, options, model, simdata, simops):
        types = {ELASTIC_CROSS_SECTION.mott_czyzewski1990: CROSS_SECTION_MOTT_JOY,
                 ELASTIC_CROSS_SECTION.mott_drouin1993: CROSS_SECTION_MOTT_EQUATION,
                 ELASTIC_CROSS_SECTION.mott_browning1994: CROSS_SECTION_MOTT_BROWNING,
                 ELASTIC_CROSS_SECTION.rutherford: CROSS_SECTION_MOTT_RUTHERFORD}
        simops.setElasticCrossSectionType(types[model])

    def _model_ionization_cross_section(self, options, model, simdata, simops):
        types = {IONIZATION_CROSS_SECTION.gauvin: IONIZATION_CROSS_SECTION_GAUVIN,
                 IONIZATION_CROSS_SECTION.pouchou1986: IONIZATION_CROSS_SECTION_POUCHOU,
                 IONIZATION_CROSS_SECTION.brown_powell: IONIZATION_CROSS_SECTION_BROWN_POWELL,
                 IONIZATION_CROSS_SECTION.casnati1982: IONIZATION_CROSS_SECTION_CASNATI,
                 IONIZATION_CROSS_SECTION.gryzinsky: IONIZATION_CROSS_SECTION_GRYZINSKI,
                 IONIZATION_CROSS_SECTION.jakoby: IONIZATION_CROSS_SECTION_JAKOBY}
        simops.setIonizationCrossSectionType(types[model])

    def _model_ionization_potential(self, options, model, simdata, simops):
        types = {IONIZATION_POTENTIAL.joy_luo1989: IONIZATION_POTENTIAL_JOY,
                 IONIZATION_POTENTIAL.berger_seltzer1983: IONIZATION_POTENTIAL_BERGER,
                 IONIZATION_POTENTIAL.hovington: IONIZATION_POTENTIAL_HOVINGTON}
        simops.setIonizationPotentialType(types[model])

    def _model_random_number_generator(self, options, model, simdata, simops):
        types = {RANDOM_NUMBER_GENERATOR.press1966_rand1: RANDOM_NUMBER_GENERATOR_PRESS_ET_AL,
                 RANDOM_NUMBER_GENERATOR.mersenne: RANDOM_NUMBER_GENERATOR_MERSENNE_TWISTER}
        simops.setRandomNumberGeneratorType(types[model])

    def _model_direction_cosine(self, options, model, simdata, simops):
        types = {DIRECTION_COSINE.soum1979: DIRECTION_COSINES_SOUM,
               DIRECTION_COSINE.drouin1996: DIRECTION_COSINES_DROUIN}
        simops.setDirectionCosines(types[model])

    def _model_energy_loss(self, options, model, simdata, simops):
        types = {ENERGY_LOSS.joy_luo1989: ENERGY_LOSS_JOY_LUO}
        simops.setEnergyLossType(types[model])

    def _model_mass_absorption_coefficient(self, options, model, simdata, simops):
        pass

