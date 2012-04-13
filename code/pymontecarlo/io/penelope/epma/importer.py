#!/usr/bin/env python
"""
================================================================================
:mod:`importer` -- PENEPMA importer
================================================================================

.. module:: importer
   :synopsis: PENEPMA importer

.. inheritance-diagram:: pymontecarlo.io.penelope.epma.importer

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
from pymontecarlo.io.base.importer import ImporterException
from pymontecarlo.io.penelope.importer import Importer as _Importer
from pymontecarlo.result.base.result import \
    (
    PhotonIntensityResult,
    ElectronFractionResult,
    TimeResult,
    create_intensity_dict,
    )
from pymontecarlo.input.base.detector import \
    (
#     BackscatteredElectronEnergyDetector,
#     BackscatteredElectronPolarAngularDetector,
#     PhiRhoZDetector,
#     PhotonIntensityDetector,
     PhotonSpectrumDetector,
     ElectronFractionDetector,
     TimeDetector,
     )
from pymontecarlo.util.transition import Transition

# Globals and constants variables.
from pymontecarlo.result.base.result import \
    EMITTED, NOFLUORESCENCE, CHARACTERISTIC, BREMSSTRAHLUNG, TOTAL

def _read_intensities_line(line):
        values = line.split()

        try:
            transition = Transition(z=int(values[0]),
                                    src=int(values[2]),
                                    dest=int(values[1]))
        except ValueError: # transition not supported
            return None, 0.0, 0.0, 0.0, 0.0

        nf = float(values[4]), float(values[5])
        cf = float(values[6]), float(values[7])
        bf = float(values[8]), float(values[9])
        #tf = float(values[10]), float(values[11])
        t = float(values[12]), float(values[13])

        return transition, cf, bf, nf, t

class Importer(_Importer):

    def __init__(self):
        _Importer.__init__(self)

        self._detector_importers[PhotonSpectrumDetector] = \
            self._detector_photon_spectrum
#        self._detector_importers[ElectronFractionDetector] = \
#            self._detector_electron_fraction
#        self._detector_importers[TimeDetector] = self._detector_time

    def _detector_photon_spectrum(self, options, key, detector, path):
        # Find detector index
        keys = sorted(options.detectors.findall(PhotonSpectrumDetector).keys())
        index = keys.index(key) + 1

        # Find data files
        emitted_filepath = os.path.join(path, 'pe-inten-%s.dat' % str(index).zfill(2))
        if not os.path.exists(emitted_filepath):
            raise ImporterException, "Data file %s cannot be found" % emitted_filepath

        generated_filepath = os.path.join(path, 'pe-gen-ph.dat')
        if not os.path.exists(generated_filepath):
            raise ImporterException, "Data file %s cannot be found" % generated_filepath

        # Load generated
        intensities = {}

        with open(generated_filepath, 'r') as fp:
            for line in fp:
                line = line.strip()
                if line.startswith('#'): continue

                transition, gcf, gbf, gnf, gt = _read_intensities_line(line)

                if transition is not None:
                    tmpintensities = \
                        create_intensity_dict(transition, gcf, gbf, gnf, gt)
                    intensities.update(tmpintensities)

        # Load emitted
        with open(emitted_filepath, 'r') as fp:
            for line in fp:
                line = line.strip()
                if line.startswith('#'): continue

                transition, ecf, ebf, enf, et = _read_intensities_line(line)

                if transition is not None:
                    tmpintensities = intensities[transition]
                    tmpintensities[EMITTED][CHARACTERISTIC] = ecf
                    tmpintensities[EMITTED][BREMSSTRAHLUNG] = ebf
                    tmpintensities[EMITTED][NOFLUORESCENCE] = enf
                    tmpintensities[EMITTED][TOTAL] = et

        return PhotonIntensityResult(detector, intensities)

    def _detector_electron_fraction(self, options, key, detector, path):
        pass

    def _detector_time(self, options, key, detector, path):
        pass
