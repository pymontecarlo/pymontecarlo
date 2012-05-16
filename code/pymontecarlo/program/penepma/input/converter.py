#!/usr/bin/env python
"""
================================================================================
:mod:`converter` -- PENEPMA conversion from base options
================================================================================

.. module:: converter
   :synopsis: PENEPMA conversion from base options

.. inheritance-diagram:: pymontecarlo.program.penepma.input.converter

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import warnings

# Third party modules.

# Local modules.
from pymontecarlo.input.converter import ConversionWarning
from pymontecarlo.program.penelope.input.converter import \
    Converter as _Converter, ConversionException

from pymontecarlo.input.beam import GaussianBeam, PencilBeam
from pymontecarlo.input.limit import TimeLimit, ShowersLimit, UncertaintyLimit
from pymontecarlo.input.detector import \
    (
#     BackscatteredElectronAzimuthalAngularDetector,
#     BackscatteredElectronEnergyDetector,
#     BackscatteredElectronPolarAngularDetector,
#     EnergyDepositedSpatialDetector,
#     PhiRhoZDetector,
#     PhotonAzimuthalAngularDetector,
     PhotonIntensityDetector,
#     PhotonPolarAngularDetector,
     PhotonSpectrumDetector,
#     TransmittedElectronAzimuthalAngularDetector,
#     TransmittedElectronEnergyDetector,
#     TransmittedElectronPolarAngularDetector
     ElectronFractionDetector,
     TimeDetector,
     )

# Globals and constants variables.

class Converter(_Converter):
    BEAMS = [GaussianBeam]
    DETECTORS = [
#                 BackscatteredElectronAzimuthalAngularDetector,
#                 BackscatteredElectronEnergyDetector,
#                 BackscatteredElectronPolarAngularDetector,
#                 EnergyDepositedSpatialDetector,
#                 PhiRhoZDetector,
#                 PhotonAzimuthalAngularDetector,
#                 PhotonPolarAngularDetector,
                 PhotonSpectrumDetector,
#                 TransmittedElectronAzimuthalAngularDetector,
#                 TransmittedElectronEnergyDetector,
#                 TransmittedElectronPolarAngularDetector,
                 ElectronFractionDetector,
                 TimeDetector,
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

    def _convert_beam(self, options):
        try:
            _Converter._convert_beam(self, options)
        except ConversionException as ex:
            if isinstance(options.beam, PencilBeam):
                old = options.beam
                options.beam = GaussianBeam(old.energy_eV, 0.0, old.origin_m,
                                            old.direction, old.aperture_rad)

                message = "Pencil beam converted to Gaussian beam with 0 m diameter"
                warnings.warn(message, ConversionWarning)
            else:
                raise ex

    def _convert_detectors(self, options):
        # Create PhotonSpectrumDetector for PhotonIntensityDetectors
        dets = options.detectors.findall(PhotonIntensityDetector)
        for key, det in dets.iteritems():
            newdet = PhotonSpectrumDetector(det.elevation_rad, det.azimuth_rad,
                                            (0.0, options.beam.energy_eV), 1000)
            options.detectors[key] = newdet

            message = "Replaced PhotonIntensityDetector (%s) with a PhotonSpectrumDetector" % key
            warnings.warn(message, ConversionWarning)

        # Superclass convert
        _Converter._convert_detectors(self, options)

        # Check that no photon detector have the same delimited limit
        dets = options.detectors.findall(PhotonSpectrumDetector)

        limits = {}
        for key, det in dets.iteritems():
            limit = det.elevation_rad + det.azimuth_rad

            for otherkey, otherlimit in limits.iteritems():
                if limit == otherlimit:
                    raise ConversionException, \
                        "Detector (%s) has the same opening as detector (%s)" % \
                            (key, otherkey)

            limits[key] = limit

    def _convert_limits(self, options):
        _Converter._convert_limits(self, options)

        if not options.limits:
            raise ConversionException, "At least one limit must be defined."

