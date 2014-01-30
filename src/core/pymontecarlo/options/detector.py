#!/usr/bin/env python
"""
================================================================================
:mod:`detector` -- Basic parameters about X-ray and electron detectors
================================================================================

.. module:: detector
   :synopsis: Basic parameters about X-ray and electron detectors

.. inheritance-diagram:: pymontecarlo.input.detector

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

__all__ = ['BackscatteredElectronAzimuthalAngularDetector',
           'BackscatteredElectronEnergyDetector',
           'BackscatteredElectronPolarAngularDetector',
           'BackscatteredElectronRadialDetector',
           'ElectronFractionDetector',
           'EnergyDepositedSpatialDetector',
           'PhotonDepthDetector',
           'PhotonRadialDetector',
           'PhotonAzimuthalAngularDetector',
           'PhotonIntensityDetector',
           'PhotonPolarAngularDetector',
           'PhotonSpectrumDetector',
           'PhotonEmissionMapDetector',
           'ShowersStatisticsDetector',
           'TimeDetector',
           'TrajectoryDetector',
           'TransmittedElectronAzimuthalAngularDetector',
           'TransmittedElectronEnergyDetector',
           'TransmittedElectronPolarAngularDetector']

# Standard library modules.
import math
import itertools

# Third party modules.
import numpy as np

# Local modules.
from pymontecarlo.util.human import camelcase_to_words
from pymontecarlo.util.parameter import \
    (ParameterizedMetaclass, Parameter, AngleParameter, UnitParameter,
     range_validator)

# Globals and constants variables.
HALFPI = math.pi / 2.0
TWOPI = math.pi * 2.0
TOLERANCE = 1e-6

def equivalent_opening(det1, det2, places=6):
    """
    Returns whether two delimited detectors have the same opening.
    """
    if round(abs(det2.elevation_rad[0] - det1.elevation_rad[0]), places) > 0:
        return False

    if round(abs(det2.elevation_rad[1] - det1.elevation_rad[1]), places) > 0:
        return False

    if round(abs(det2.azimuth_rad[0] - det1.azimuth_rad[0]), places) > 0:
        return False

    if round(abs(det2.azimuth_rad[1] - det1.azimuth_rad[1]), places) > 0:
        return False

    return True

class _Detector(object, metaclass=ParameterizedMetaclass):

    def __repr__(self):
        return '<%s()>' % self.__class__.__name__

    def __str__(self):
        return '%s' % camelcase_to_words(self.__class__.__name__)

def _elevation_validator(value):
    if value.lower >= value.upper:
        raise ValueError("Lower value '%s' greater or equal to upper value '%s'" % \
                         (value.lower, value.upper))
    range_validator(-HALFPI - TOLERANCE, HALFPI + TOLERANCE)(value.lower)
    range_validator(-HALFPI - TOLERANCE, HALFPI + TOLERANCE)(value.upper)

def _azimuth_validator(value):
    if value.lower >= value.upper:
        raise ValueError("Lower value '%s' greater or equal to upper value '%s'" % \
                         (value.lower, value.upper))
    range_validator(0, TWOPI + TOLERANCE)(value.lower)
    range_validator(0, TWOPI + TOLERANCE)(value.upper)

class _DelimitedDetector(_Detector):

    elevation = AngleParameter(_elevation_validator, ('lower', 'upper'),
                               doc="Elevation angle from the x-y plane")
    azimuth = AngleParameter(_azimuth_validator, ('lower', 'upper'),
                             doc="Azimuth angle from the positive x-axis")

    def __init__(self, elevation_rad, azimuth_rad):
        """
        Creates a new detector.

        A detector is defined by its position: elevation and azimuth.

        The *elevation* is the angle from the x-y plane, aka the take-off angle.
        A positive elevation is above the x-y plane (towards positive z) and a
        negative elevation is below the x-y plane (towards negative z).
        The elevation can therefore vary between [-pi/2, pi/2] rad.

        The *azimuth* is the counter-clockwise angle from the positive x-axis in
        the x-y plane.
        It can vary between [0, 2pi] rad.

        :arg elevation_rad: elevation limits
        :type elevation_rad: :class:`tuple`

        :arg azimuth_rad: azimuth limits
        :type azimuth_rad: :class:`tuple`
        """
        _Detector.__init__(self)

        self.elevation_rad = elevation_rad
        self.azimuth_rad = azimuth_rad

    def __repr__(self):
        return '<%s(elevation=%s to %s deg, azimuth=%s to %s deg)>' % \
            (self.__class__.__name__,
             self.elevation_deg.lower, self.elevation_deg.upper,
             self.azimuth_deg.lower, self.azimuth_deg.upper)

    def __unicode__(self):
        return '%s (elevation=%s to %s \u00b0, azimuth=%s to %s \u00b0)' % \
            (camelcase_to_words(self.__class__.__name__),
             self.elevation_deg.lower, self.elevation_deg.upper,
             self.azimuth_deg.lower, self.azimuth_deg.upper)

    @classmethod
    def annular(cls, takeoffangle_rad, opening_rad):
        takeoffangles = np.array(takeoffangle_rad, ndmin=1)
        openings = np.array(opening_rad, ndmin=1)

        elevations = []
        for takeoffangle, opening in itertools.product(takeoffangles, openings):
            elevation = (takeoffangle - opening, takeoffangle + opening)
            elevations.append(elevation)

        return cls(elevations, (0.0, 2.0 * math.pi))

    @property
    def solidangle_sr(self):
        elevations = np.array(self.elevation_rad, ndmin=1)
        azimuths = np.array(self.azimuth_rad, ndmin=1)

        solidangles = []
        for elevation, azimuth in itertools.product(elevations, azimuths):
            solidangle = abs((azimuth[1] - azimuth[0]) * \
                             (math.cos(elevation[0]) - math.cos(elevation[1])))
            solidangles.append(solidangle)

        if len(solidangles) == 1:
            return solidangles[0]
        else:
            return solidangles

    @property
    def takeoffangle_rad(self):
        elevation = self.elevation_rad
        return (elevation.lower + elevation.upper) / 2.0

    @property
    def takeoffangle_deg(self):
        return np.degrees(self.takeoffangle_rad)

class _ChannelsDetector(_Detector):

    channels = Parameter(np.int, range_validator(1.0), doc="Number of channels")

    def __init__(self, channels):
        _Detector.__init__(self)
        self.channels = channels

    def __repr__(self):
        return '<%s(channels=%s)>' % (self.__class__.__name__, self.channels)

    def __unicode__(self):
        return '%s (channels=%s)' % \
            (camelcase_to_words(self.__class__.__name__), self.channels)

class _SpatialDetector(_Detector):

    xlimits = UnitParameter('m', fields=('lower', 'upper'), doc="Limits in x")
    xbins = Parameter(np.int, range_validator(1.0), doc="Number of bins in x")
    ylimits = UnitParameter('m', fields=('lower', 'upper'), doc="Limits in y")
    ybins = Parameter(np.int, range_validator(1.0), doc="Number of bins in y")
    zlimits = UnitParameter('m', fields=('lower', 'upper'), doc="Limits in z")
    zbins = Parameter(np.int, range_validator(1.0), doc="Number of bins in z")

    def __init__(self, xlimits_m, xbins, ylimits_m, ybins, zlimits_m, zbins):
        _Detector.__init__(self)

        self.xlimits_m = xlimits_m
        self.ylimits_m = ylimits_m
        self.zlimits_m = zlimits_m

        self.xbins = xbins
        self.ybins = ybins
        self.zbins = zbins

    def __repr__(self):
        return "<%s(x=%s to %s m (%s), y=%s to %s m (%s), z=%s to %s m (%s))>" % \
            (self.__class__.__name__,
             self.xlimits_m.lower, self.xlimits_m.upper, self.xbins,
             self.ylimits_m.lower, self.ylimits_m.upper, self.ybins,
             self.zlimits_m.lower, self.zlimits_m.upper, self.zbins)

    def __unicode__(self):
        return "%s (x=%s to %s nm (%s), y=%s to %s nm (%s), z=%s to %s nm (%s))" % \
            (camelcase_to_words(self.__class__.__name__),
             self.xlimits_m.lower * 1e9, self.xlimits_m.upper * 1e9, self.xbins,
             self.ylimits_m.lower * 1e9, self.ylimits_m.upper * 1e9, self.ybins,
             self.zlimits_m.lower * 1e9, self.zlimits_m.upper * 1e9, self.zbins)

def _energy_limit_validator(value):
    if value.lower >= value.upper:
        raise ValueError("Lower value '%s' greater or equal to upper value '%s'" % \
                         (value.lower, value.upper))
    range_validator(0.0)(value.lower)
    range_validator(0.0)(value.upper)

class _EnergyDetector(_ChannelsDetector):

    limits = UnitParameter('eV', _energy_limit_validator, ('lower', 'upper'),
                           doc="Energy limits (in eV)")

    def __init__(self, channels, limits_eV):
        _ChannelsDetector.__init__(self, channels)
        self.limits_eV = limits_eV

    def __repr__(self):
        return "<%s(limits=%s to %s eV, channels=%s)>" % \
            (self.__class__.__name__,
             self.limits_eV.lower, self.limits_eV.upper, self.channels)

    def __unicode__(self):
        return '%s (limits=%s to %s eV, channels=%s)' % \
            (camelcase_to_words(self.__class__.__name__),
             self.limits_eV.lower, self.limits_eV.upper, self.channels)

class _AngularDetector(_ChannelsDetector):

    def __init__(self, channels, limits_rad):
        _ChannelsDetector.__init__(self, channels)
        self.limits_rad = limits_rad

    def __repr__(self):
        return "<%s(limits=%s to %s rad, channels=%s)>" % \
            (self.__class__.__name__,
             self.limits_rad.lower, self.limits_rad.upper, self.channels)

    def __unicode__(self):
        return u"%s (limits=%s to %s \u00b0, channels=%s)>" % \
            (camelcase_to_words(self.__class__.__name__),
             self.limits_rad.lower, self.limits_rad.upper, self.channels)

class _PolarAngularDetector(_AngularDetector):

    limits = AngleParameter(_elevation_validator, ('lower', 'upper'),
                            doc="Angular limits (in radians)")

    def __init__(self, channels, limits_rad=(-HALFPI, HALFPI)):
        _AngularDetector.__init__(self, channels, limits_rad)

class _AzimuthalAngularDetector(_AngularDetector):

    limits = AngleParameter(_azimuth_validator, ('lower', 'upper'),
                            doc="Angular limits (in radians)")

    def __init__(self, channels, limits_rad=(0, TWOPI)):
        _AngularDetector.__init__(self, channels, limits_rad)
#
class _PhotonDelimitedDetector(_DelimitedDetector):
    pass

class BackscatteredElectronEnergyDetector(_EnergyDetector):
    pass

class TransmittedElectronEnergyDetector(_EnergyDetector):
    pass

class BackscatteredElectronPolarAngularDetector(_PolarAngularDetector):
    pass

class TransmittedElectronPolarAngularDetector(_PolarAngularDetector):
    pass

class BackscatteredElectronAzimuthalAngularDetector(_AzimuthalAngularDetector):
    pass

class TransmittedElectronAzimuthalAngularDetector(_AzimuthalAngularDetector):
    pass

class BackscatteredElectronRadialDetector(_ChannelsDetector):
    pass

class PhotonPolarAngularDetector(_PolarAngularDetector):
    pass

class PhotonAzimuthalAngularDetector(_AzimuthalAngularDetector):
    pass

class EnergyDepositedSpatialDetector(_SpatialDetector):
    pass

class PhotonSpectrumDetector(_PhotonDelimitedDetector, _EnergyDetector):

    def __init__(self, elevation_rad, azimuth_rad, channels, limits_eV):
        _PhotonDelimitedDetector.__init__(self, elevation_rad, azimuth_rad)
        _EnergyDetector.__init__(self, channels, limits_eV)

    @classmethod
    def annular(cls, takeoffangle_rad, opening_rad, limits_eV, channels):
        tmpdet = _PhotonDelimitedDetector.annular(takeoffangle_rad, opening_rad)
        return cls(tmpdet.elevation_rad, tmpdet.azimuth_rad, limits_eV, channels)

    def __repr__(self):
        return "<%s(elevation=%s to %s deg, azimuth=%s to %s deg, limits=%s to %s eV, channels=%s)>" % \
            (self.__class__.__name__,
             self.elevation_deg.lower, self.elevation_deg.upper,
             self.azimuth_deg.lower, self.azimuth_deg.upper,
             self.limits_eV.lower, self.limits_eV.upper,
             self.channels)

    def __unicode__(self):
        return u"%s (elevation=%s to %s \u00b0, azimuth=%s to %s \u00b0, limits=%s to %s eV, channels=%s)" % \
            (camelcase_to_words(self.__class__.__name__),
             self.elevation_deg.lower, self.elevation_deg.upper,
             self.azimuth_deg.lower, self.azimuth_deg.upper,
             self.limits_eV.lower, self.limits_eV.upper,
             self.channels)

class PhotonDepthDetector(_PhotonDelimitedDetector, _ChannelsDetector):

    def __init__(self, elevation_rad, azimuth_rad, channels):
        _ChannelsDetector.__init__(self, channels)
        _PhotonDelimitedDetector.__init__(self, elevation_rad, azimuth_rad)

    @classmethod
    def annular(cls, takeoffangle_rad, opening_rad, channels):
        tmpdet = _PhotonDelimitedDetector.annular(takeoffangle_rad, opening_rad)
        return cls(tmpdet.elevation_rad, tmpdet.azimuth_rad, channels)

    def __repr__(self):
        return '<%s(elevation=%s to %s deg, azimuth=%s to %s deg, channels=%s)>' % \
            (self.__class__.__name__,
             self.elevation_deg.lower, self.elevation_deg.upper,
             self.azimuth_deg.lower, self.azimuth_deg.upper,
             self.channels)

    def __unicode__(self):
        return u'%s (elevation=%s to %s \u00b0, azimuth=%s to %s \u00b0, channels=%s)' % \
            (camelcase_to_words(self.__class__.__name__),
             self.elevation_deg.lower, self.elevation_deg.upper,
             self.azimuth_deg.lower, self.azimuth_deg.upper,
             self.channels)

class PhotonRadialDetector(_PhotonDelimitedDetector, _ChannelsDetector):

    def __init__(self, elevation_rad, azimuth_rad, channels):
        _ChannelsDetector.__init__(self, channels)
        _PhotonDelimitedDetector.__init__(self, elevation_rad, azimuth_rad)

    @classmethod
    def annular(cls, takeoffangle_rad, opening_rad, channels):
        tmpdet = _PhotonDelimitedDetector.annular(takeoffangle_rad, opening_rad)
        return cls(tmpdet.elevation_rad, tmpdet.azimuth_rad, channels)

    def __repr__(self):
        return '<%s(elevation=%s to %s deg, azimuth=%s to %s deg, channels=%s)>' % \
            (self.__class__.__name__,
             self.elevation_deg.lower, self.elevation_deg.upper,
             self.azimuth_deg.lower, self.azimuth_deg.upper,
             self.channels)

    def __unicode__(self):
        return u'%s (elevation=%s to %s \u00b0, azimuth=%s to %s \u00b0, channels=%s)' % \
            (self.__class__.__name__,
             self.elevation_deg.lower, self.elevation_deg.upper,
             self.azimuth_deg.lower, self.azimuth_deg.upper,
             self.channels)

class PhotonEmissionMapDetector(_PhotonDelimitedDetector):

    xbins = Parameter(np.int, range_validator(1.0), doc="Number of bins in x")
    ybins = Parameter(np.int, range_validator(1.0), doc="Number of bins in y")
    zbins = Parameter(np.int, range_validator(1.0), doc="Number of bins in z")

    def __init__(self, elevation_rad, azimuth_rad, xbins, ybins, zbins):
        _PhotonDelimitedDetector.__init__(self, elevation_rad, azimuth_rad)

        self.xbins = xbins
        self.ybins = ybins
        self.zbins = zbins

    @classmethod
    def annular(cls, takeoffangle_rad, opening_rad, xbins, ybins, zbins):
        tmpdet = _PhotonDelimitedDetector.annular(takeoffangle_rad, opening_rad)
        return cls(tmpdet.elevation_rad, tmpdet.azimuth_rad, xbins, ybins, zbins)

    def __repr__(self):
        return '<%s(elevation=%s to %s deg, azimuth=%s to %s deg, bins=(%s, %s, %s))>' % \
            (self.__class__.__name__,
             self.elevation_deg.lower, self.elevation_deg.upper,
             self.azimuth_deg.lower, self.azimuth_deg.upper,
             self.xbins, self.ybins, self.zbins)

    def __unicode__(self):
        return u'%s (elevation=%s to %s \u00b0, azimuth=%s to %s \u00b0, bins=(%s, %s, %s))' % \
            (camelcase_to_words(self.__class__.__name__),
             self.elevation_deg.lower, self.elevation_deg.upper,
             self.azimuth_deg.lower, self.azimuth_deg.upper,
             self.xbins, self.ybins, self.zbins)

class PhotonIntensityDetector(_PhotonDelimitedDetector):
    pass

class TimeDetector(_Detector):
    """
    Records simulation time and speed (electron simulated /s).
    """
    pass

class ElectronFractionDetector(_Detector):
    """
    Records backscattered, transmitted and absorbed fraction of primary electrons.
    """
    pass

class ShowersStatisticsDetector(_Detector):
    """
    Records number of simulated particles.
    """
    pass

class TrajectoryDetector(_Detector):
    """
    Records the trajectories of particles.
    """

    secondary = Parameter(doc="Whether to simulate secondary particles")

    def __init__(self, secondary=True):
        """
        Creates a detector of trajectories.

        .. note::

           The number of trajectories is defined by the :class:`ShowerLimit`

        :arg secondary: whether to simulate secondary particles
        :type secondary: :class:`bool`
        """
        _Detector.__init__(self)
        self.secondary = secondary

    def __repr__(self):
        prep = 'with' if self.secondary else 'without'
        return '<%s(%s secondary particles)>' % (self.__class__.__name__, prep)

    def __unicode__(self):
        prep = 'with' if self.secondary else 'without'
        return '%s (%s secondary particles)' % \
            (camelcase_to_words(self.__class__.__name__), prep)

