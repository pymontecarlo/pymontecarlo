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

# Local modules.
from pymontecarlo.output.importer import Importer as _Importer
from pymontecarlo.output.result import \
    (
    PhotonIntensityResult,
    ElectronFractionResult,
    create_intensity_dict,
    )
from pymontecarlo.input.detector import \
    (
#     BackscatteredElectronEnergyDetector,
#     BackscatteredElectronPolarAngularDetector,
#     PhiRhoZDetector,
     PhotonIntensityDetector,
     ElectronFractionDetector,
#     TransmittedElectronEnergyDetector,
     )
from pymontecarlo.util.transition import K_family, LIII, MV

from casinoTools.FileFormat.casino2.File import File

# Globals and constants variables.
from casinoTools.FileFormat.casino2.Element import \
    LINE_K, LINE_L, LINE_M, GENERATED, EMITTED

LINE_LOOKUP = {LINE_K: K_family, LINE_L: LIII, LINE_M: MV}

class Importer(_Importer):

    def __init__(self):
        _Importer.__init__(self)

        self._detector_importers[PhotonIntensityDetector] = \
            self._detector_photon_intensity
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

                gt = (datum[GENERATED] * factor, 0.0)
                et = (datum[EMITTED] * factor, 0.0)

                tmpints = create_intensity_dict(transition,
                                                gnf=gt, gt=gt,
                                                enf=et, et=et)
                intensities.update(tmpints)

        return PhotonIntensityResult(intensities)

    def _detector_electron_fraction(self, options, name, detector, simdata):
        bse_intensity = simdata.getSimulationResults().BE_Intensity[0]
        return ElectronFractionResult(backscattered=(bse_intensity, 0.0))



