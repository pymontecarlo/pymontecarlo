#!/usr/bin/env python
"""
================================================================================
:mod:`exporter` -- Exporter to CAS file
================================================================================

.. module:: exporter
   :synopsis: Exporter to CAS file

.. inheritance-diagram:: pymontecarlo.input.casino2.exporter

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from operator import attrgetter
import math

# Third party modules.
from pkg_resources import resource_stream #@UnresolvedImport
import numpy as np

# Local modules.
from pymontecarlo.input.base.exporter import Exporter, ExporterException
from pymontecarlo.input.base.beam import GaussianBeam
from pymontecarlo.input.base.geometry import \
    Substrate, MultiLayers, GrainBoundaries
from pymontecarlo.input.base.limit import ShowersLimit
from pymontecarlo.input.base.detector import \
    (BackscatteredElectronEnergyDetector,
     BackscatteredElectronPolarAngularDetector,
     PhiRhoZDetector,
     PhotonIntensityDetector,
     TransmittedElectronEnergyDetector,
     )
import pymontecarlo.util.element_properties as ep

from casinoTools.FileFormat.casino2.File import File

# Globals and constants variables.

class Casino2Exporter(Exporter):

    def __init__(self):
        Exporter.__init__(self)

        self._beam_exporters[GaussianBeam] = self._beam_gaussian

        self._detector_exporters[BackscatteredElectronEnergyDetector] = \
            self._detector_backscattered_electron_energy
        self._detector_exporters[BackscatteredElectronPolarAngularDetector] = \
            self._detector_backscattered_electron_polar_angular
        self._detector_exporters[TransmittedElectronEnergyDetector] = \
            self._detector_transmitted_electron_energy
        self._detector_exporters[PhiRhoZDetector] = \
            self._detector_phirhoz
        self._detector_exporters[PhotonIntensityDetector] = \
            self._detector_photon_intensity

        self._limit_exporters[ShowersLimit] = self._limit_showers

    def export(self, options):
        casfile = File()

        # Load template (from geometry)
        fileobj = self._get_sim_template(options)
        casfile.readFromFileObject(fileobj)

        simdata = casfile.getOptionSimulationData()
        simops = simdata.getSimulationOptions()

        self._export(options, simdata, simops)

        return casfile

    def _get_sim_template(self, options):
        geometry = options.geometry
        geometry_name = geometry.__class__.__name__

        if isinstance(geometry, Substrate):
            return resource_stream(__name__, "templates/Substrate.sim")
        elif isinstance(geometry, (MultiLayers, GrainBoundaries)):
            regions_count = len(geometry.get_bodies())

            try:
                return resource_stream(__name__, "templates/%s%i.sim" % (geometry_name, regions_count))
            except IOError:
                raise ExporterException, "No template for '%s' with region count: %i" % \
                    (geometry_name, regions_count)
        else:
            raise ExporterException, "Unknown geometry: %s" % geometry_name

    def _export_geometry(self, options, simdata, simops):
        geometry = options.geometry

        regionops = simdata.getRegionOptions()

        # Material composition and density
        for i, body in enumerate(geometry.get_bodies()):
            material = body.material
            region = regionops.getRegion(i)

            region.removeAllElements()

            for z, fraction in material.composition.iteritems():
                region.addElement(ep.symbol(z), weightFraction=fraction)

            region.update() # Calculate number of elements, mean atomic number

            region.User_Density = True
            region.Rho = material.density
            region.Name = material.name

        # Thickness
        if isinstance(geometry, MultiLayers):
            layers = geometry.layers

            for i, layer in enumerate(layers):
                dim = geometry.get_dimensions(layer)
                parameters = [abs(dim.zmax) * 1e9, abs(dim.zmin) * 1e9, 0.0, 0.0]
                regionops.getRegion(i).setParameters(parameters)

            if geometry.has_substrate():
                dim = geometry.get_dimensions(geometry.substrate_body)
                region = regionops.getRegion(regionops.getNumberRegions() - 1)

                parameters = region.getParameters()
                parameters[0] = abs(dim.zmax) * 1e9
                parameters[2] = parameters[0] + 10.0
                region.setParameters(parameters)

        elif isinstance(geometry, GrainBoundaries):
            layers = geometry.layers
            assert len(layers) == regionops.getNumberRegions() - 2 # without substrates

            # Left substrate
            region = regionops.getRegion(0)
            dim = geometry.get_dimensions(geometry.left_body)
            parameters = region.getParameters()
            parameters[1] = dim.xmax * 1e9
            parameters[2] = parameters[1] - 10.0
            region.setParameters(parameters)

            # Layers
            for i, layer in enumerate(layers):
                dim = geometry.get_dimensions(layer)
                parameters = [dim.xmin * 1e9, dim.xmax * 1e9, 0.0, 0.0]
                regionops.getRegion(i + 1).setParameters(parameters)

            # Right substrate
            region = regionops.getRegion(regionops.getNumberRegions() - 1)
            dim = geometry.get_dimensions(geometry.right_body)
            parameters = region.getParameters()
            parameters[0] = dim. xmin * 1e9
            parameters[2] = parameters[0] + 10.0
            region.setParameters(parameters)

        # Absorption energy electron
        abs_electron = min(map(attrgetter('absorption_energy_electron'),
                               geometry.get_materials()))
        simops.Eminimum = abs_electron / 1000.0 # keV

    def _export_detectors(self, options, simdata, simops):
        simops.RangeFinder = 3 # Fixed range
        simops.FEmissionRX = 0 # Do not simulate x-rays

        Exporter._export_detectors(self, options, simdata, simops)

        # Detector position
        dets = {}
        dets.update(options.detectors.findall(PhotonIntensityDetector))
        dets.update(options.detectors.findall(PhiRhoZDetector))
        if dets:
            detector = dets.values()[0] # There should be at least one

            simops.TOA = math.degrees(detector.takeoffangle) # deg
            simops.PhieRX = math.degrees(sum(detector.azimuth) / 2.0) # deg

    def _beam_gaussian(self, options, beam, simdata, simops):
        simops.setIncidentEnergy_keV(beam.energy / 1000.0) # keV
        simops.setPosition(beam.origin[0] * 1e9) # nm

        # Beam diameter
        # Casino's beam diameter contains 99.9% of the electrons (n=3.290)
        # d_{CASINO} = 2 (3.2905267 \sigma)
        # d_{FWHM} = 2 (1.177411 \sigma)
        # d_{CASINO} = 2.7947137 d_{FWHM}
        simops.Beam_Diameter = 2.7947137 * beam.diameter * 1e9 # nm

        # Beam tilt
        a = np.array(beam.direction)
        b = np.array([0, 0, -1])
        angle = np.arccos(np.vdot(a, b) / np.linalg.norm(a))
        simops.Beam_angle = math.degrees(angle)

    def _detector_backscattered_electron_energy(self, options, name,
                                                detector, simdata, simops):
        simops.FDenr = 1
        simops.FDenrLog = 0
        simops.NbPointDENR = detector.channels
        simops.DenrMin = detector.limits[0] / 1000.0 # keV
        simops.DenrMax = detector.limits[1] / 1000.0 # keV

    def _detector_transmitted_electron_energy(self, options, name,
                                              detector, simdata, simops):
        simops.FDent = 1
        simops.FDentLog = 0
        simops.NbPointDENT = detector.channels
        simops.DentMin = detector.limits[0] / 1000.0 # keV
        simops.DentMax = detector.limits[1] / 1000.0 # keV

    def _detector_backscattered_electron_polar_angular(self, options, name,
                                                       detector, simdata, simops):
        simops.FDbang = 1
        simops.FDbangLog = 0
        simops.NbPointDBANG = detector.channels
        simops.DbangMin = math.degrees(detector.limits[0]) # deg
        simops.DbangMax = math.degrees(detector.limits[1]) # deg

    def _detector_phirhoz(self, options, name, detector, simdata, simops):
        # FIXME: Casino freezes when this value is set
        #simops.NbreCoucheRX = detector.channels
        simops.FEmissionRX = 1 # Simulate x-ray

    def _detector_photon_intensity(self, options, name, detector, simdata, simops):
        simops.FEmissionRX = 1 # Simulate x-rays

    def _limit_showers(self, options, limit, simdata, simops):
        simops.setNumberElectrons(limit.showers)

