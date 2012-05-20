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

# Third party modules.

# Local modules.
from pymontecarlo.io.importer import Importer as _Importer
from pymontecarlo.output.result import \
    (
    PhotonIntensityResult,
    PhiRhoZResult,
    ElectronFractionResult,
    TimeResult,
    create_intensity_dict,
    )
from pymontecarlo.input.detector import \
    (
#     BackscatteredElectronEnergyDetector,
#     BackscatteredElectronPolarAngularDetector,
     PhiRhoZDetector,
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
from winxrayTools.ResultsFile.CharateristicPhirhoz import CharateristicPhirhoz

# Globals and constants variables.
from winxrayTools.ResultsFile.CharacteristicIntensity import \
    EMITTED as WXREMITTED, GENERATED as WXRGENERATED
from pymontecarlo.output.result import EMITTED, GENERATED, NOFLUORESCENCE, TOTAL

class Importer(_Importer):

    def __init__(self):
        _Importer.__init__(self)

        self._detector_importers[PhotonIntensityDetector] = \
            self._detector_photon_intensity
        self._detector_importers[PhiRhoZDetector] = \
            self._detector_phirhoz
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
            gt = data[WXRGENERATED]
            et = data[WXREMITTED]

            tmpints = create_intensity_dict(transition,
                                            gnf=gt, gt=gt,
                                            enf=et, et=et)
            intensities.update(tmpints)

        return PhotonIntensityResult(intensities)

    def _detector_phirhoz(self, options, name, detector, path):
        wxrresult = CharateristicPhirhoz(path)
        distributions = {}

        def _extract(data, key, dists):
            for z in data:
                for xrayline in data[z]:
                    transition = from_string(symbol(z) + " " + xrayline)

                    zs, vals, uncs = data[z][xrayline]
                    zs = [val * 1e-9 for val in zs]

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
