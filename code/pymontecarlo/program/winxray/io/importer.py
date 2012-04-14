#!/usr/bin/env python
"""
================================================================================
:mod:`importer` -- WinX-Ray results importer
================================================================================

.. module:: importer
   :synopsis: WinX-Ray results importer

.. inheritance-diagram:: pymontecarlo.result.winxray.importer

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os

# Third party modules.

# Local modules.
from pymontecarlo.io.importer import Importer as _Importer
from pymontecarlo.result.result import \
    (
    PhotonIntensityResult,
    ElectronFractionResult,
    TimeResult,
    create_intensity_dict,
    )
from pymontecarlo.input.detector import \
    (
#     BackscatteredElectronEnergyDetector,
#     BackscatteredElectronPolarAngularDetector,
#     PhiRhoZDetector,
     PhotonIntensityDetector,
#     PhotonSpectrumDetector,
     ElectronFractionDetector,
     TimeDetector,
     )
from pymontecarlo.util.element_properties import symbol
from pymontecarlo.util.transition import from_string

from winxrayTools.ResultsFile.BseResults import BseResults
from winxrayTools.ResultsFile.GeneralResults import GeneralResults
from winxrayTools.ResultsFile.CharacteristicIntensity import CharacteristicIntensity

# Globals and constants variables.
from winxrayTools.ResultsFile.CharacteristicIntensity import EMITTED, GENERATED

class Importer(_Importer):

    def __init__(self):
        _Importer.__init__(self)

        self._detector_importers[PhotonIntensityDetector] = \
            self._detector_photon_intensity
        self._detector_importers[ElectronFractionDetector] = \
            self._detector_electron_fraction
        self._detector_importers[TimeDetector] = self._detector_time

    def import_from_dir(self, options, path):
        """
        Imports WinX-Ray results from a results directory.
        
        :arg options: options of the simulation
        :type options: :class:`Options <pymontecarlo.input.base.options.Options>`
        
        :arg path: location of the results directory
        """
        if not os.path.isdir(path):
            raise ValueError, "Specified path (%s) is not a directory" % path

        return self._import_results(options, path)

    def _detector_photon_intensity(self, options, name, detector, path):
        wxrresult = CharacteristicIntensity(path)

        intensities = {}

        for z, line in wxrresult.getAtomicNumberLines():
            data = wxrresult.intensities[z][line]
            transition = from_string("%s %s" % (symbol(z), line))

            # FIXME: Normalize WinX-Ray intensity
            gt = data[GENERATED]
            et = data[EMITTED]

            tmpints = create_intensity_dict(transition,
                                            gnf=gt, gt=gt,
                                            enf=et, et=et)
            intensities.update(tmpints)

        return PhotonIntensityResult(detector, intensities)

    def _detector_electron_fraction(self, options, name, detector, path):
        wxrresult = BseResults(path)

        backscattered = wxrresult.getBseYield(), wxrresult.getBseYieldError()

        return ElectronFractionResult(detector, backscattered=backscattered)

    def _detector_time(self, options, name, detector, path):
        wxrresult = GeneralResults(path)

        simulation_time_s = wxrresult.time_s
        simulation_speed_s = simulation_time_s / wxrresult.numberElectron, 0.0

        return TimeResult(detector, simulation_time_s, simulation_speed_s)
