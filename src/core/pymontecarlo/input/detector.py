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
from collections import namedtuple

# Third party modules.

# Local modules.
from pymontecarlo.input.parameter import \
    (ParameterizedMetaClass, Parameter, AngleParameter, UnitParameter,
     SimpleValidator, CastValidator)
#from pymontecarlo.util.xmlutil import XMLIO
from pymontecarlo.util.human import camelcase_to_words
from pymontecarlo.util.mathutil import _vector

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

class limit(_vector, namedtuple('limits', ['lower', 'upper'])):

    def __new__(cls, lower, upper):
        return cls.__bases__[1].__new__(cls, min(lower, upper), max(lower, upper))

    @property
    def low(self):
        return self.lower

    @property
    def high(self):
        return self.upper

class _Detector(object):

    __metaclass__ = ParameterizedMetaClass
    
    def __repr__(self):
        return '<%s()>' % self.__class__.__name__

    def __unicode__(self):
        return '%s' % camelcase_to_words(self.__class__.__name__)

_equality_validator = \
    SimpleValidator(lambda x: abs(x.high - x.low) > TOLERANCE,
                    "Elevation angles cannot be equal")
_elevation_validator = \
    SimpleValidator(lambda x:-HALFPI <= x.low <= HALFPI and -HALFPI <= x.high <= HALFPI,
                    "Angle must be between [-pi/2, pi/2] rad")
_azimuth_validator = \
    SimpleValidator(lambda x: 0 <= x.low <= TWOPI and 0 <= x.high <= TWOPI,
                    "Angle must be between [0, 2pi] rad")

class _DelimitedDetector(_Detector):
    
    elevation = AngleParameter([CastValidator(limit),
                                _equality_validator,
                                _elevation_validator],
                               "Elevation angle from the x-y plane")
    azimuth = AngleParameter([CastValidator(limit),
                              _equality_validator,
                              _azimuth_validator],
                               "Azimuth angle from the positive x-axis")
    
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
             self.elevation_deg[0], self.elevation_deg[1],
             self.azimuth_deg[0], self.azimuth_deg[1])

    def __str__(self):
        return '%s (elevation=%s to %s deg, azimuth=%s to %s deg)' % \
            (camelcase_to_words(self.__class__.__name__),
             self.elevation_deg[0], self.elevation_deg[1],
             self.azimuth_deg[0], self.azimuth_deg[1])

    def __unicode__(self):
        return u'%s (elevation=%s to %s \u00b0, azimuth=%s to %s \u00b0)' % \
            (camelcase_to_words(self.__class__.__name__),
             self.elevation_deg[0], self.elevation_deg[1],
             self.azimuth_deg[0], self.azimuth_deg[1])

#    @classmethod
#    def __loadxml__(cls, element, *args, **kwargs):
#        elevation = (float(element.get('elevation_min')),
#                     float(element.get('elevation_max')))
#        azimuth = (float(element.get('azimuth_min')),
#                   float(element.get('azimuth_max')))
#
#        return cls(elevation, azimuth)
#
#    def __savexml__(self, element, *args, **kwargs):
#        element.set('elevation_min', str(self.elevation_rad[0]))
#        element.set('elevation_max', str(self.elevation_rad[1]))
#
#        element.set('azimuth_min', str(self.azimuth_rad[0]))
#        element.set('azimuth_max', str(self.azimuth_rad[1]))

    @classmethod
    def annular(cls, takeoffangle_rad, opening_rad):
        elevation_rad = (takeoffangle_rad - opening_rad, takeoffangle_rad + opening_rad)
        azimuth_rad = (0.0, 2.0 * math.pi)
        return cls(elevation_rad, azimuth_rad)

    @property
    def solidangle_sr(self):
        return abs((self.azimuth_rad[1] - self.azimuth_rad[0]) * \
                   (math.cos(self.elevation_rad[0]) - math.cos(self.elevation_rad[1])))

    @property
    def takeoffangle_rad(self):
        return sum(self.elevation_rad) / 2.0

    @property
    def takeoffangle_deg(self):
        return math.degrees(self.takeoffangle_rad)

_bins_validator = \
    SimpleValidator(lambda x: x >= 1,
                    'Number of channels must be greater or equal to 1')

class _ChannelsDetector(_Detector):

    channels = Parameter(_bins_validator, "Number of channels")

    def __init__(self, channels):
        _Detector.__init__(self)
        self.channels = channels

    def __repr__(self):
        return '<%s(channels=%s)>' % (self.__class__.__name__, self.channels)

    def __unicode__(self):
        return '%s (channels=%s)' % \
            (camelcase_to_words(self.__class__.__name__), self.channels)

#    @classmethod
#    def __loadxml__(cls, element, *args, **kwargs):
#        channels = int(element.get('channels'))
#        return cls(channels)
#
#    def __savexml__(self, element, *args, **kwargs):
#        element.set('channels', str(self.channels))

#class _BoundedChannelsDetector(_ChannelsDetector):
#
#    def __init__(self, extremums=(float('-inf'), float('inf'))):
#        _ChannelsDetector.__init__(self, 1)
#        self._extremums = extremums
#
#    def __repr__(self):
#        limits = self._props['limits']
#        return '<%s(limits=%s to %s, channels=%s)>' % \
#            (self.__class__.__name__, limits[0], limits[1], self.channels)
#
##    @classmethod
##    def __loadxml__(cls, element, *args, **kwargs):
##        limits = float(element.get('limit_min')), float(element.get('limit_max'))
##        channels = int(element.get('channels'))
##
##        return cls(limits, channels)
##
##    def __savexml__(self, element, *args, **kwargs):
##        limits = self._props['limits']
##
##        element.set('limit_min', str(limits[0]))
##        element.set('limit_max', str(limits[1]))
##        element.set('channels', str(self.channels))
#
#    def _set_limits(self, limits):
#        low, high = limits
#
#        if abs(high - low) < TOLERANCE:
#            raise ValueError, "Upper and lower limits are equal"
#        if low < self._extremums[0] - TOLERANCE or low > self._extremums[1] + TOLERANCE:
#            raise ValueError, "Lower limit (%s) must be between [%s, %s]." % \
#                (low, self._extremums[0], self._extremums[1])
#        if high < self._extremums[0] - TOLERANCE or high > self._extremums[1] + TOLERANCE:
#            raise ValueError, "Upper limit (%s) must be between [%s, %s]." % \
#                (high, self._extremums[0], self._extremums[1])
#
#        self._props['limits'] = min(low, high), max(low, high)
#
#    def _get_limits(self):
#        return self._props['limits']

class _SpatialDetector(_Detector):

    xlimits = UnitParameter('m', doc="Limits in x")
    xbins = Parameter(_bins_validator, "Number of bins in x")
    ylimits = UnitParameter('m', doc="Limits in y")
    ybins = Parameter(_bins_validator, "Number of bins in y")
    zlimits = UnitParameter('m', doc="Limits in z")
    zbins = Parameter(_bins_validator, "Number of bins in z")

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
             self.xlimits_m[0], self.xlimits_m[1], self.xbins,
             self.ylimits_m[0], self.ylimits_m[1], self.ybins,
             self.zlimits_m[0], self.zlimits_m[1], self.zbins)

    def __unicode__(self):
        return "%s (x=%s to %s nm (%s), y=%s to %s nm (%s), z=%s to %s nm (%s))" % \
            (camelcase_to_words(self.__class__.__name__),
             self.xlimits_m[0] * 1e9, self.xlimits_m[1] * 1e9, self.xbins,
             self.ylimits_m[0] * 1e9, self.ylimits_m[1] * 1e9, self.ybins,
             self.zlimits_m[0] * 1e9, self.zlimits_m[1] * 1e9, self.zbins)

#    @classmethod
#    def __loadxml__(cls, element, *args, **kwargs):
#        xlimits = float(element.get('xlimit_min')), float(element.get('xlimit_max'))
#        xbins = int(element.get('xbins'))
#
#        ylimits = float(element.get('ylimit_min')), float(element.get('ylimit_max'))
#        ybins = int(element.get('ybins'))
#
#        zlimits = float(element.get('zlimit_min')), float(element.get('zlimit_max'))
#        zbins = int(element.get('zbins'))
#
#        return cls(xlimits, xbins, ylimits, ybins, zlimits, zbins)
#
#    def __savexml__(self, element, *args, **kwargs):
#        element.set('xlimit_min', str(self.xlimits_m[0]))
#        element.set('xlimit_max', str(self.xlimits_m[1]))
#        element.set('xbins', str(self.xbins))
#
#        element.set('ylimit_min', str(self.ylimits_m[0]))
#        element.set('ylimit_max', str(self.ylimits_m[1]))
#        element.set('ybins', str(self.ybins))
#
#        element.set('zlimit_min', str(self.zlimits_m[0]))
#        element.set('zlimit_max', str(self.zlimits_m[1]))
#        element.set('zbins', str(self.zbins))

_energy_limit_validator = \
    SimpleValidator(lambda x: x[0] >= 0 and x[1] >= 0,
                    "Energy must be greater or equal to 0.0")

class _EnergyDetector(_ChannelsDetector):

    limits = UnitParameter('eV',
                           [CastValidator(limit), _energy_limit_validator],
                           "Energy limits (in eV)")

    def __init__(self, limits_eV, channels):
        _ChannelsDetector.__init__(self, channels)
        self.limits_eV = limits_eV

    def __repr__(self):
        return "<%s(limits=%s to %s eV, channels=%s)>" % \
            (self.__class__.__name__, self.limits_eV[0], self.limits_eV[1], self.channels)

    def __unicode__(self):
        return '%s (limits=%s to %s eV, channels=%s)' % \
            (camelcase_to_words(self.__class__.__name__),
             self.limits_eV[0], self.limits_eV[1], self.channels)

class _AngularDetector(_ChannelsDetector):

    def __init__(self, channels, limits_rad):
        _ChannelsDetector.__init__(self, channels)
        self.limits_rad = limits_rad

    def __repr__(self):
        return "<%s(limits=%s to %s rad, channels=%s)>" % \
            (self.__class__.__name__, self.limits_rad[0], self.limits_rad[1], self.channels)

    def __unicode__(self):
        return u"%s (limits=%s to %s \u00b0, channels=%s)>" % \
            (camelcase_to_words(self.__class__.__name__),
             self.limits_deg[0], self.limits_deg[1], self.channels)

#    @classmethod
#    def __loadxml__(cls, element, *args, **kwargs):
#        # Required due to argument inversion
#        limits = float(element.get('limit_min')), float(element.get('limit_max'))
#        channels = int(element.get('channels'))
#
#        return cls(channels, limits)

class _PolarAngularDetector(_AngularDetector):

    limits = AngleParameter([CastValidator(limit), _elevation_validator],
                            "Angular limits (in radians)")

    def __init__(self, channels, limits_rad=(-HALFPI, HALFPI)):
        _AngularDetector.__init__(self, channels, limits_rad)

class _AzimuthalAngularDetector(_AngularDetector):

    limits = AngleParameter([CastValidator(limit), _azimuth_validator],
                            "Angular limits (in radians)")

    def __init__(self, channels, limits_rad=(0, TWOPI)):
        _AngularDetector.__init__(self, channels, limits_rad)

class _PhotonDelimitedDetector(_DelimitedDetector):
    pass

class BackscatteredElectronEnergyDetector(_EnergyDetector):
    pass

#XMLIO.register('{http://pymontecarlo.sf.net}backscatteredElectronEnergyDetector', BackscatteredElectronEnergyDetector)

class TransmittedElectronEnergyDetector(_EnergyDetector):
    pass

#XMLIO.register('{http://pymontecarlo.sf.net}transmittedElectronEnergyDetector', TransmittedElectronEnergyDetector)

class BackscatteredElectronPolarAngularDetector(_PolarAngularDetector):
    pass

#XMLIO.register('{http://pymontecarlo.sf.net}backscatteredElectronPolarAngularDetector', BackscatteredElectronPolarAngularDetector)

class TransmittedElectronPolarAngularDetector(_PolarAngularDetector):
    pass

#XMLIO.register('{http://pymontecarlo.sf.net}transmittedElectronPolarAngularDetector', TransmittedElectronPolarAngularDetector)

class BackscatteredElectronAzimuthalAngularDetector(_AzimuthalAngularDetector):
    pass

#XMLIO.register('{http://pymontecarlo.sf.net}backscatteredElectronAzimuthalAngularDetector', BackscatteredElectronAzimuthalAngularDetector)

class TransmittedElectronAzimuthalAngularDetector(_AzimuthalAngularDetector):
    pass

#XMLIO.register('{http://pymontecarlo.sf.net}transmittedElectronAzimuthalAngularDetector', TransmittedElectronAzimuthalAngularDetector)

class BackscatteredElectronRadialDetector(_ChannelsDetector):
    pass

#XMLIO.register('{http://pymontecarlo.sf.net}backscatteredElectronRadialDetector', BackscatteredElectronRadialDetector)

class PhotonPolarAngularDetector(_PolarAngularDetector):
    pass

#XMLIO.register('{http://pymontecarlo.sf.net}photonPolarAngularDetector', PhotonPolarAngularDetector)

class PhotonAzimuthalAngularDetector(_AzimuthalAngularDetector):
    pass

#XMLIO.register('{http://pymontecarlo.sf.net}photonAzimuthalAngularDetector', PhotonAzimuthalAngularDetector)

class EnergyDepositedSpatialDetector(_SpatialDetector):

    def __init__(self, xlimits_m, xbins, ylimits_m, ybins, zlimits_m, zbins):
        _SpatialDetector.__init__(self, xlimits_m, xbins,
                                        ylimits_m, ybins,
                                        zlimits_m, zbins)

#XMLIO.register('{http://pymontecarlo.sf.net}energyDepositedSpatialDetector', EnergyDepositedSpatialDetector)

class PhotonSpectrumDetector(_PhotonDelimitedDetector, _EnergyDetector):

    def __init__(self, elevation_rad, azimuth_rad, limits_eV, channels):
        _PhotonDelimitedDetector.__init__(self, elevation_rad, azimuth_rad)
        _EnergyDetector.__init__(self, limits_eV, channels)

    def __repr__(self):
        return "<%s(elevation=%s to %s deg, azimuth=%s to %s deg, limits=%s to %s eV, channels=%s)>" % \
            (self.__class__.__name__,
             self.elevation_deg[0], self.elevation_deg[1],
             self.azimuth_deg[0], self.azimuth_deg[1],
             self.limits_eV[0], self.limits_eV[1],
             self.channels)

    def __unicode__(self):
        return u"%s (elevation=%s to %s \u00b0, azimuth=%s to %s \u00b0, limits=%s to %s eV, channels=%s)" % \
            (camelcase_to_words(self.__class__.__name__),
             self.elevation_deg[0], self.elevation_deg[1],
             self.azimuth_deg[0], self.azimuth_deg[1],
             self.limits_eV[0], self.limits_eV[1],
             self.channels)

#    @classmethod
#    def __loadxml__(cls, element, *args, **kwargs):
#        delimited = _PhotonDelimitedDetector.__loadxml__(element, *args, **kwargs)
#        energy = _EnergyDetector.__loadxml__(element, *args, **kwargs)
#
#        return cls(delimited.elevation_rad, delimited.azimuth_rad,
#                   energy.limits_eV, energy.channels)
#
#    def __savexml__(self, element, *args, **kwargs):
#        _PhotonDelimitedDetector.__savexml__(self, element, *args, **kwargs)
#        _EnergyDetector.__savexml__(self, element, *args, **kwargs)

#XMLIO.register('{http://pymontecarlo.sf.net}photonSpectrumDetector', PhotonSpectrumDetector)

class PhotonDepthDetector(_PhotonDelimitedDetector, _ChannelsDetector):

    def __init__(self, elevation_rad, azimuth_rad, channels):
        _ChannelsDetector.__init__(self, channels)
        _PhotonDelimitedDetector.__init__(self, elevation_rad, azimuth_rad)

    def __repr__(self):
        return '<%s(elevation=%s to %s deg, azimuth=%s to %s deg, channels=%s)>' % \
            (self.__class__.__name__,
             self.elevation_deg[0], self.elevation_deg[1],
             self.azimuth_deg[0], self.azimuth_deg[1],
             self.channels)

    def __unicode__(self):
        return u'%s (elevation=%s to %s \u00b0, azimuth=%s to %s \u00b0, channels=%s)' % \
            (camelcase_to_words(self.__class__.__name__),
             self.elevation_deg[0], self.elevation_deg[1],
             self.azimuth_deg[0], self.azimuth_deg[1],
             self.channels)

#    @classmethod
#    def __loadxml__(cls, element, *args, **kwargs):
#        delimited = _PhotonDelimitedDetector.__loadxml__(element, *args, **kwargs)
#        channels = _ChannelsDetector.__loadxml__(element, *args, **kwargs)
#        return cls(delimited.elevation_rad, delimited.azimuth_rad, channels.channels)
#
#    def __savexml__(self, element, *args, **kwargs):
#        _PhotonDelimitedDetector.__savexml__(self, element, *args, **kwargs)
#        _ChannelsDetector.__savexml__(self, element, *args, **kwargs)

#XMLIO.register('{http://pymontecarlo.sf.net}photonDepthDetector', PhotonDepthDetector)

class PhotonRadialDetector(_PhotonDelimitedDetector, _ChannelsDetector):

    def __init__(self, elevation_rad, azimuth_rad, channels):
        _ChannelsDetector.__init__(self, channels)
        _PhotonDelimitedDetector.__init__(self, elevation_rad, azimuth_rad)

    def __repr__(self):
        return '<%s(elevation=%s to %s deg, azimuth=%s to %s deg, channels=%s)>' % \
            (self.__class__.__name__,
             self.elevation_deg[0], self.elevation_deg[1],
             self.azimuth_deg[0], self.azimuth_deg[1],
             self.channels)

    def __unicode__(self):
        return u'%s (elevation=%s to %s \u00b0, azimuth=%s to %s \u00b0, channels=%s)' % \
            (self.__class__.__name__,
             self.elevation_deg[0], self.elevation_deg[1],
             self.azimuth_deg[0], self.azimuth_deg[1],
             self.channels)

#    @classmethod
#    def __loadxml__(cls, element, *args, **kwargs):
#        delimited = _PhotonDelimitedDetector.__loadxml__(element, *args, **kwargs)
#        channels = _ChannelsDetector.__loadxml__(element, *args, **kwargs)
#        return cls(delimited.elevation_rad, delimited.azimuth_rad, channels.channels)
#
#    def __savexml__(self, element, *args, **kwargs):
#        _PhotonDelimitedDetector.__savexml__(self, element, *args, **kwargs)
#        _ChannelsDetector.__savexml__(self, element, *args, **kwargs)

#XMLIO.register('{http://pymontecarlo.sf.net}photonRadialDetector', PhotonRadialDetector)

class PhotonEmissionMapDetector(_PhotonDelimitedDetector):

    xbins = Parameter(_bins_validator, "Number of bins in x")
    ybins = Parameter(_bins_validator, "Number of bins in y")
    zbins = Parameter(_bins_validator, "Number of bins in z")

    def __init__(self, elevation_rad, azimuth_rad, xbins, ybins, zbins):
        _PhotonDelimitedDetector.__init__(self, elevation_rad, azimuth_rad)

        self.xbins = xbins
        self.ybins = ybins
        self.zbins = zbins

    def __repr__(self):
        return '<%s(elevation=%s to %s deg, azimuth=%s to %s deg, bins=(%s, %s, %s))>' % \
            (self.__class__.__name__,
             self.elevation_deg[0], self.elevation_deg[1],
             self.azimuth_deg[0], self.azimuth_deg[1],
             self.xbins, self.ybins, self.zbins)

    def __unicode__(self):
        return u'%s (elevation=%s to %s \u00b0, azimuth=%s to %s \u00b0, bins=(%s, %s, %s))' % \
            (camelcase_to_words(self.__class__.__name__),
             self.elevation_deg[0], self.elevation_deg[1],
             self.azimuth_deg[0], self.azimuth_deg[1],
             self.xbins, self.ybins, self.zbins)

#    @classmethod
#    def __loadxml__(cls, element, *args, **kwargs):
#        delimited = _PhotonDelimitedDetector.__loadxml__(element, *args, **kwargs)
#        xbins = int(element.get('xbins'))
#        ybins = int(element.get('ybins'))
#        zbins = int(element.get('zbins'))
#        return cls(delimited.elevation_rad, delimited.azimuth_rad,
#                   xbins, ybins, zbins)
#
#    def __savexml__(self, element, *args, **kwargs):
#        _PhotonDelimitedDetector.__savexml__(self, element, *args, **kwargs)
#        element.set('xbins', str(self.xbins))
#        element.set('ybins', str(self.ybins))
#        element.set('zbins', str(self.zbins))

#XMLIO.register('{http://pymontecarlo.sf.net}photonEmissionMapDetector', PhotonEmissionMapDetector)

class PhotonIntensityDetector(_PhotonDelimitedDetector):
    pass

#XMLIO.register('{http://pymontecarlo.sf.net}photonIntensityDetector', PhotonIntensityDetector)

class TimeDetector(_Detector):
    """
    Records simulation time and speed (electron simulated /s).
    """
    pass

#XMLIO.register('{http://pymontecarlo.sf.net}timeDetector', TimeDetector)

class ElectronFractionDetector(_Detector):
    """
    Records backscattered, transmitted and absorbed fraction of primary electrons.
    """
    pass

#XMLIO.register('{http://pymontecarlo.sf.net}electronFractionDetector', ElectronFractionDetector)

class ShowersStatisticsDetector(_Detector):
    """
    Records number of simulated particles.
    """
    pass

#XMLIO.register('{http://pymontecarlo.sf.net}showersStatisticsDetector', ShowersStatisticsDetector)

class TrajectoryDetector(_Detector):
    """
    Records the trajectories of particles.
    """

    secondary = Parameter(CastValidator(bool),
                          "Whether to simulate secondary particles")

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

#    @classmethod
#    def __loadxml__(cls, element, *args, **kwargs):
#        secondary = True if element.get('secondary') == 'true' else False
#
#        return cls(secondary)
#
#    def __savexml__(self, element, *args, **kwargs):
#        element.set('secondary', str(self.secondary).lower())

#XMLIO.register('{http://pymontecarlo.sf.net}trajectoryDetector', TrajectoryDetector)

