#!/usr/bin/env python
"""
================================================================================
:mod:`importer` -- Casino 2 results importer
================================================================================

.. module:: importer
   :synopsis: Casino 2 results importer

.. inheritance-diagram:: pymontecarlo.program.casino2.output.importer

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.
import numpy as np

# Local modules.
from pymontecarlo.output.importer import Importer as _Importer
from pymontecarlo.output.result import \
    (
    PhotonIntensityResult,
    ElectronFractionResult,
    create_intensity_dict,
    PhotonDepthResult,
    PhotonRadialResult,
    create_photondist_dict,
    )
from pymontecarlo.input.detector import \
    (
#     BackscatteredElectronEnergyDetector,
#     BackscatteredElectronPolarAngularDetector,
     PhotonDepthDetector,
     PhotonRadialDetector,
     PhotonIntensityDetector,
     ElectronFractionDetector,
#     TransmittedElectronEnergyDetector,
     )
from pymontecarlo.util.transition import K_family, LIII, MV

from casinoTools.FileFormat.casino2.File import File

# Globals and constants variables.
from casinoTools.FileFormat.casino2.Element import \
    LINE_K, LINE_L, LINE_M, GENERATED as CAS_GENERATED, EMITTED as CAS_EMITTED
from pymontecarlo.output.result import GENERATED, EMITTED, NOFLUORESCENCE, TOTAL

LINE_LOOKUP = {LINE_K: K_family, LINE_L: LIII, LINE_M: MV}

class Importer(_Importer):

    def __init__(self):
        _Importer.__init__(self)

        self._detector_importers[PhotonIntensityDetector] = \
            self._detector_photon_intensity
        self._detector_importers[PhotonDepthDetector] = \
            self._detector_photon_depth
        self._detector_importers[PhotonRadialDetector] = \
            self._detector_photon_radial
        self._detector_importers[ElectronFractionDetector] = \
            self._detector_electron_fraction

    def import_from_cas(self, options, fileobj):
        # Read cas
        casfile = File()
        casfile.readFromFileObject(fileobj)

        simdata = casfile.getResultsFirstSimulation()

        return self._import_results(options, simdata)

    def _detector_photon_intensity(self, options, name, detector, simdata):
        cas_intensities = simdata.getTotalXrayIntensities()
        factor = detector.solidangle_sr / (0.0025 * 1e9)
        if factor == 0.0: factor = 1.0

        intensities = {}
        for z in cas_intensities:
            for line in cas_intensities[z]:
                transition = LINE_LOOKUP[line](z)
                datum = cas_intensities[z][line]

                gt = (datum[CAS_GENERATED] * factor, 0.0)
                et = (datum[CAS_EMITTED] * factor, 0.0)

                tmpints = create_intensity_dict(transition,
                                                gnf=gt, gt=gt,
                                                enf=et, et=et)
                intensities.update(tmpints)

        return PhotonIntensityResult(intensities)

    def _detector_photon_depth(self, options, name, detector, simdata):
        simops = simdata.getSimulationOptions()
        dz = simops.EpaisCouche * 1e-9 # nm
        nz = simops.NbreCoucheRX
        zs = np.linspace(-nz * dz, 0.0, nz - 1, True)

        dists = {}

        for region in simdata.getRegionOptions().getRegions():
            for element in region.getElements():
                z = element.getAtomicNumber()
                delta = element.getDepthXrayDistribution()

                for line in delta.keys():
                    transition = LINE_LOOKUP[line](z)

                    delta_gnf = delta[line][CAS_GENERATED][::-1]
                    delta_enf = delta[line][CAS_EMITTED][::-1]

                    if transition in dists:
                        gnf = dists[transition][GENERATED][NOFLUORESCENCE]
                        gnf[:, 1] += delta_gnf

                        gt = dists[transition][GENERATED][TOTAL]
                        gt[:, 1] += delta_gnf

                        enf = dists[transition][EMITTED][NOFLUORESCENCE]
                        enf[:, 1] += delta_enf
                        et = dists[transition][EMITTED][TOTAL]
                        et[:, 1] += delta_enf
                    else:
                        gnf = np.array([zs, delta_gnf]).transpose()
                        enf = np.array([zs, delta_enf]).transpose()
                        dists.update(create_photondist_dict(transition,
                                                            gnf, gnf, enf, enf))

        return PhotonDepthResult(dists)

    def _detector_photon_radial(self, options, name, detector, simdata):
        simops = simdata.getSimulationOptions()
        dr = simops.EpaisCouche * 1e-9 # nm
        nr = simops.NbreCoucheRX
        rs = np.linspace(0.0, dr * nr, nr, True)

        areas = np.pi * (rs[1:] ** 2 - rs[:-1] ** 2)
        rs = rs[:-1]

        dists = {}

        for region in simdata.getRegionOptions().getRegions():
            for element in region.getElements():
                z = element.getAtomicNumber()
                delta = element.getRadialXrayDistribution()

                for line in delta.keys():
                    transition = LINE_LOOKUP[line](z)

                    delta_gnf = delta[line][CAS_GENERATED] / areas
                    delta_enf = delta[line][CAS_EMITTED] / areas

                    if transition in dists:
                        gnf = dists[transition][GENERATED][NOFLUORESCENCE]
                        gnf[:, 1] += delta_gnf

                        gt = dists[transition][GENERATED][TOTAL]
                        gt[:, 1] += delta_gnf

                        enf = dists[transition][EMITTED][NOFLUORESCENCE]
                        enf[:, 1] += delta_enf
                        et = dists[transition][EMITTED][TOTAL]
                        et[:, 1] += delta_enf
                    else:
                        gnf = np.array([rs, delta_gnf]).transpose()
                        enf = np.array([rs, delta_enf]).transpose()
                        dists.update(create_photondist_dict(transition,
                                                            gnf, gnf, enf, enf))

        return PhotonRadialResult(dists)

    def _detector_electron_fraction(self, options, name, detector, simdata):
        bse_intensity = simdata.getSimulationResults().BE_Intensity[0]
        return ElectronFractionResult(backscattered=(bse_intensity, 0.0))



