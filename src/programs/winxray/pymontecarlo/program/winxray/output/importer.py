#!/usr/bin/env python
"""
================================================================================
:mod:`importer` -- WinX-Ray results importer
================================================================================

.. module:: importer
   :synopsis: WinX-Ray results importer

.. inheritance-diagram:: pymontecarlo.program.winxray.output.importer

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
from operator import mul

# Third party modules.
import numpy as np

from pyxray.element_properties import symbol
from pyxray.transition import from_string

# Local modules.
from pymontecarlo.output.importer import Importer as _Importer
from pymontecarlo.output.result import \
    (
    PhotonIntensityResult,
    PhotonSpectrumResult,
    PhotonDepthResult,
    ElectronFractionResult,
    TimeResult,
    create_intensity_dict,
    ShowersStatisticsResult,
    )
from pymontecarlo.input.detector import \
    (
#     BackscatteredElectronEnergyDetector,
#     BackscatteredElectronPolarAngularDetector,
     PhotonDepthDetector,
     PhotonIntensityDetector,
     PhotonSpectrumDetector,
     ElectronFractionDetector,
     TimeDetector,
     ShowersStatisticsDetector,
     )
from pymontecarlo.input.limit import ShowersLimit

from winxrayTools.ResultsFile.BseResults import BseResults
from winxrayTools.ResultsFile.GeneralResults import GeneralResults
from winxrayTools.ResultsFile.CharacteristicIntensity import CharacteristicIntensity
from winxrayTools.ResultsFile.CharateristicPhirhoz import CharateristicPhirhoz
from winxrayTools.ResultsFile.XRaySpectrum import XRaySpectrum

# Globals and constants variables.
from winxrayTools.ResultsFile.CharacteristicIntensity import \
    EMITTED as WXREMITTED, GENERATED as WXRGENERATED
from winxrayTools.ResultsFile.XRaySpectrum import \
    (ENERGY as WXRSPC_ENERGY,
     TOTAL as WXRSPC_TOTAL,
     BACKGROUND as WXRSPC_BACKGROUND)
from pymontecarlo.output.result import EMITTED, GENERATED, NOFLUORESCENCE, TOTAL

class Importer(_Importer):

    def __init__(self):
        _Importer.__init__(self)

        self._detector_importers[PhotonIntensityDetector] = \
            self._detector_photon_intensity
        self._detector_importers[PhotonSpectrumDetector] = \
            self._detector_photon_spectrum
        self._detector_importers[PhotonDepthDetector] = \
            self._detector_photondepth
        self._detector_importers[ElectronFractionDetector] = \
            self._detector_electron_fraction
        self._detector_importers[TimeDetector] = self._detector_time
        self._detector_importers[ShowersStatisticsDetector] = \
            self._detector_showers_statistics

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

    def _get_normalization_factor(self, options, detector):
        """
        Returns the factor that should be *multiplied* to WinXRay intensities
        to convert them to counts / (sr.electron).
        """
        nelectron = options.limits.find(ShowersLimit).showers
        solidangle_sr = detector.solidangle_sr
        return 1.0 / (nelectron * solidangle_sr)

    def _detector_photon_intensity(self, options, name, detector, path):
        wxrresult = CharacteristicIntensity(path)
        factor = self._get_normalization_factor(options, detector)

        # Retrieve intensities
        intensities = {}

        for z, line in wxrresult.getAtomicNumberLines():
            data = wxrresult.intensities[z][line]
            transition = from_string("%s %s" % (symbol(z), line))

            gt = map(mul, data[WXRGENERATED], [factor] * 2)
            et = map(mul, data[WXREMITTED], [factor] * 2)

            tmpints = create_intensity_dict(transition,
                                            gnf=gt, gt=gt,
                                            enf=et, et=et)
            intensities.update(tmpints)

        return PhotonIntensityResult(intensities)

    def _detector_photon_spectrum(self, options, name, detector, path):
        wxrresult = XRaySpectrum(path)

        # Retrieve data
        energies = np.array(wxrresult.data[WXRSPC_ENERGY])
        total = np.array([energies, wxrresult.data[WXRSPC_TOTAL]]).T
        background = np.array([energies, wxrresult.data[WXRSPC_BACKGROUND]]).T

        # Arrange units
        factor = self._get_normalization_factor(options, detector)
        factor /= energies[1] - energies[0]

        total[:, 1] *= factor
        background[:, 1] *= factor

        return PhotonSpectrumResult(total, background)

    def _detector_photondepth(self, options, name, detector, path):
        wxrresult = CharateristicPhirhoz(path)
        distributions = {}

        def _extract(data, key, dists):
            for z in data:
                for xrayline in data[z]:
                    transition = from_string(symbol(z) + " " + xrayline)

                    dist = np.array(data[z][xrayline]).T

                    # Convert z values in meters
                    dist[:, 0] *= -1e-9

                    # WinXRay starts from the bottom to the top
                    # The order must be reversed
                    dist = dist[::-1]

                    dists.setdefault(transition, {}).setdefault(key, {})
                    dists[transition][key][NOFLUORESCENCE] = dist
                    dists[transition][key][TOTAL] = dist

        _extract(wxrresult.getPhirhozs('Generated'), GENERATED, distributions)
        _extract(wxrresult.getPhirhozs('Emitted'), EMITTED, distributions)

        return PhotonDepthResult(distributions)

    def _detector_electron_fraction(self, options, name, detector, path):
        wxrresult = BseResults(path)

        backscattered = wxrresult.getBseYield(), wxrresult.getBseYieldError()

        return ElectronFractionResult(backscattered=backscattered)

    def _detector_time(self, options, name, detector, path):
        wxrresult = GeneralResults(path)

        simulation_time_s = wxrresult.time_s
        simulation_speed_s = simulation_time_s / wxrresult.numberElectron, 0.0

        return TimeResult(simulation_time_s, simulation_speed_s)

    def _detector_showers_statistics(self, options, name, detector, path):
        wxrresult = GeneralResults(path)

        showers = wxrresult.numberElectron

        return ShowersStatisticsResult(showers)
