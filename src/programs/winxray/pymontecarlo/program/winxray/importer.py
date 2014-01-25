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
from operator import mul

# Third party modules.
import numpy as np

from pyxray.element_properties import symbol
from pyxray.transition import from_string

# Local modules.
from pymontecarlo.program.importer import Importer as _Importer
from pymontecarlo.results.result import \
    (
    PhotonIntensityResult,
    PhotonSpectrumResult,
    PhotonDepthResult,
    ElectronFractionResult,
    TimeResult,
    create_intensity_dict,
    ShowersStatisticsResult,
    )
from pymontecarlo.options.detector import \
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
from pymontecarlo.options.limit import ShowersLimit

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
from pymontecarlo.results.result import EMITTED, GENERATED, NOFLUORESCENCE, TOTAL

class Importer(_Importer):

    def __init__(self):
        _Importer.__init__(self)

        self._importers[PhotonIntensityDetector] = self._import_photon_intensity
        self._importers[PhotonSpectrumDetector] = self._import_photon_spectrum
        self._importers[PhotonDepthDetector] = self._import_photondepth
        self._importers[ElectronFractionDetector] = \
            self._import_electron_fraction
        self._importers[TimeDetector] = self._import_time
        self._importers[ShowersStatisticsDetector] = \
            self._import_showers_statistics

    def _import(self, options, dirpath, *args, **kwargs):
        return self._run_importers(options, dirpath)

    def _get_normalization_factor(self, options, detector):
        """
        Returns the factor that should be *multiplied* to WinXRay intensities
        to convert them to counts / (sr.electron).
        """
        limits = list(options.limits.iterclass(ShowersLimit))
        nelectron = limits[0].showers
        solidangle_sr = detector.solidangle_sr
        return 1.0 / (nelectron * solidangle_sr)

    def _import_photon_intensity(self, options, name, detector, path):
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

    def _import_photon_spectrum(self, options, name, detector, path):
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

    def _import_photondepth(self, options, name, detector, path):
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

    def _import_electron_fraction(self, options, name, detector, path):
        wxrresult = BseResults(path)

        backscattered = wxrresult.getBseYield(), wxrresult.getBseYieldError()

        return ElectronFractionResult(backscattered=backscattered)

    def _import_time(self, options, name, detector, path):
        wxrresult = GeneralResults(path)

        simulation_time_s = wxrresult.time_s
        simulation_speed_s = simulation_time_s / wxrresult.numberElectron, 0.0

        return TimeResult(simulation_time_s, simulation_speed_s)

    def _import_showers_statistics(self, options, name, detector, path):
        wxrresult = GeneralResults(path)

        showers = wxrresult.numberElectron

        return ShowersStatisticsResult(showers)
