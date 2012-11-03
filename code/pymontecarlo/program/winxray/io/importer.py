#!/usr/bin/env python
"""
================================================================================
:mod:`importer` -- WinX-Ray results importer
================================================================================

.. module:: importer
   :synopsis: WinX-Ray results importer

.. inheritance-diagram:: pymontecarlo.program.winxray.io.importer

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

# Local modules.
from pymontecarlo.io.importer import Importer as _Importer
from pymontecarlo.output.result import \
    (
    PhotonIntensityResult,
    PhotonSpectrumResult,
    PhiRhoZResult,
    ElectronFractionResult,
    TimeResult,
    create_intensity_dict,
    ShowersStatisticsResult,
    )
from pymontecarlo.input.detector import \
    (
#     BackscatteredElectronEnergyDetector,
#     BackscatteredElectronPolarAngularDetector,
     PhiRhoZDetector,
     PhotonIntensityDetector,
     PhotonSpectrumDetector,
     ElectronFractionDetector,
     TimeDetector,
     ShowersStatisticsDetector,
     )
from pymontecarlo.input.limit import ShowersLimit
from pymontecarlo.util.element_properties import symbol
from pymontecarlo.util.transition import from_string

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
        self._detector_importers[PhiRhoZDetector] = \
            self._detector_phirhoz
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
        energies = wxrresult.data[WXRSPC_ENERGY]
        total = wxrresult.data[WXRSPC_TOTAL]
        background = wxrresult.data[WXRSPC_BACKGROUND]

        # Calculate energy offset and channel width
        energy_offset_eV = 0.0
        energy_channel_width_eV = energies[1] - energies[0]

        # Arrange units
        factor = self._get_normalization_factor(options, detector)
        factor /= energy_channel_width_eV

        total = [val * factor for val in total]
        background = [val * factor for val in background]

        return PhotonSpectrumResult(energy_offset_eV, energy_channel_width_eV,
                                    total=total, background=background)

    def _detector_phirhoz(self, options, name, detector, path):
        # Read density
        wxrresult = GeneralResults(path)
        density_kg_m3 = wxrresult.getMeanDensity_g_cm3() / 1000.0

        # Read phirhoz
        wxrresult = CharateristicPhirhoz(path)
        distributions = {}

        def _extract(data, key, dists):
            for z in data:
                for xrayline in data[z]:
                    transition = from_string(symbol(z) + " " + xrayline)

                    zs, vals, uncs = data[z][xrayline]
                    zs = [val * 1e-9 * density_kg_m3 for val in zs]

                    # WinXRay starts from the bottom to the top
                    # The order must be reversed
                    zs.reverse()
                    vals.reverse()
                    uncs.reverse()

                    dists.setdefault(transition, {}).setdefault(key, {})
                    dists[transition][key][NOFLUORESCENCE] = (zs, vals, uncs)
                    dists[transition][key][TOTAL] = (zs, vals, uncs)

        _extract(wxrresult.getPhirhozs('Generated'), GENERATED, distributions)
        _extract(wxrresult.getPhirhozs('Emitted'), EMITTED, distributions)

        return PhiRhoZResult(distributions)

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
