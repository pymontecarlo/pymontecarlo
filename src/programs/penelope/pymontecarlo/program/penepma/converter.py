#!/usr/bin/env python
"""
================================================================================
:mod:`converter` -- PENEPMA conversion from base options
================================================================================

.. module:: converter
   :synopsis: PENEPMA conversion from base options

.. inheritance-diagram:: pymontecarlo.program.penepma.options.converter

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
from pymontecarlo.program._penelope.converter import Converter as _Converter

from pymontecarlo.options.particle import ELECTRON
from pymontecarlo.options.beam import GaussianBeam, PencilBeam
from pymontecarlo.options.limit import TimeLimit, ShowersLimit, UncertaintyLimit
from pymontecarlo.options.detector import \
    (
#     BackscatteredElectronAzimuthalAngularDetector,
     BackscatteredElectronEnergyDetector,
#     BackscatteredElectronPolarAngularDetector,
#     EnergyDepositedSpatialDetector,
     PhotonDepthDetector,
#     PhotonAzimuthalAngularDetector,
     PhotonIntensityDetector,
#     PhotonPolarAngularDetector,
     PhotonSpectrumDetector,
#     TransmittedElectronAzimuthalAngularDetector,
#     TransmittedElectronEnergyDetector,
#     TransmittedElectronPolarAngularDetector
     ElectronFractionDetector,
     TimeDetector,
     ShowersStatisticsDetector,
     )

from pymontecarlo.util.expander import ExpanderSingleDetector

# Globals and constants variables.

class Converter(_Converter):
    BEAMS = [GaussianBeam]
    DETECTORS = [
#                 BackscatteredElectronAzimuthalAngularDetector,
                 BackscatteredElectronEnergyDetector,
#                 BackscatteredElectronPolarAngularDetector,
#                 EnergyDepositedSpatialDetector,
                 PhotonDepthDetector,
#                 PhotonAzimuthalAngularDetector,
#                 PhotonPolarAngularDetector,
                 PhotonSpectrumDetector,
                 PhotonIntensityDetector,
#                 TransmittedElectronAzimuthalAngularDetector,
#                 TransmittedElectronEnergyDetector,
#                 TransmittedElectronPolarAngularDetector,
                 ElectronFractionDetector,
                 TimeDetector,
                 ShowersStatisticsDetector,
                 ]
    LIMITS = [TimeLimit, ShowersLimit, UncertaintyLimit]

    def __init__(self, elastic_scattering=(0.0, 0.0),
                 cutoff_energy_inelastic=50.0,
                 cutoff_energy_bremsstrahlung=50.0):
        """
        Converter from base options to PENEPMA options.

        During the conversion, the materials are converted to :class:`PenelopeMaterial`.
        For this, the specified elastic scattering and cutoff energies are used
        as the default values in the conversion.
        """
        _Converter.__init__(self, elastic_scattering, cutoff_energy_inelastic,
                            cutoff_energy_bremsstrahlung)

        dets = [BackscatteredElectronEnergyDetector]
        self._expander = ExpanderSingleDetector(dets)

    def _convert_beam(self, options):
        if type(options.beam) is PencilBeam:
            old = options.beam
            options.beam = GaussianBeam(old.energy_eV, 0.0, old.particle,
                                        old.origin_m, old.direction,
                                        old.aperture_rad)

            self._warn("Pencil beam converted to Gaussian beam with 0 m diameter")

        if not _Converter._convert_beam(self, options):
            return False

        if options.beam.particle is not ELECTRON:
            self._warn("Beam particle must be ELECTRON",
                       "This options definition was removed.")
            return False

        return True


