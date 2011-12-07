#!/usr/bin/env python
"""
================================================================================
:mod:`importer` -- Casino 2 results importer
================================================================================

.. module:: importer
   :synopsis: Casino 2 results importer

.. inheritance-diagram:: pymontecarlo.result.casino2.importer

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
from pymontecarlo.result.base.importer import Importer as _Importer
from pymontecarlo.result.base.result import \
    PhotonIntensityResult, create_intensity_dict
from pymontecarlo.input.base.detector import \
    (
#     BackscatteredElectronEnergyDetector,
#     BackscatteredElectronPolarAngularDetector,
#     PhiRhoZDetector,
     PhotonIntensityDetector,
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
            self._detector_photon_intensity_detector

    def import_from_cas(self, options, fileobj):
        # Read cas
        casfile = File()
        casfile.readFromFileObject(fileobj)

        simresults = casfile.getResultsFirstSimulation()

        return self._import_results(options, simresults)

    def _detector_photon_intensity_detector(self, options, name, detector, simresults):
        cas_intensities = simresults.getTotalXrayIntensities()
        factor = detector.solid_angle / (0.0025 * 1e9)

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

        return PhotonIntensityResult(detector, intensities)



