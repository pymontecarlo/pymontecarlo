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

# Third party modules.

# Local modules.
from pymontecarlo.options.parameter import \
    (ParameterizedMetaClass, Parameter, AngleParameter, UnitParameter,
     SimpleValidator, CastValidator)
from pymontecarlo.options.xmlmapper import \
    mapper, ParameterizedAttribute, ParameterizedElement, PythonType, UserType
from pymontecarlo.options.bound import bound
from pymontecarlo.util.human import camelcase_to_words

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
    SimpleValidator(lambda x:-HALFPI - TOLERANCE <= x.low <= HALFPI + TOLERANCE and \
                        - HALFPI - TOLERANCE <= x.high <= HALFPI + TOLERANCE,
                    "Angle must be between [-pi/2, pi/2] rad")
_azimuth_validator = \
    SimpleValidator(lambda x: 0 <= x.low <= TWOPI + TOLERANCE and \
                        0 <= x.high <= TWOPI + TOLERANCE,
                    "Angle must be between [0, 2pi] rad")

class _DelimitedDetector(_Detector):

    elevation = AngleParameter([CastValidator(bound),
                                _equality_validator,
                                _elevation_validator],
                               "Elevation angle from the x-y plane")
    azimuth = AngleParameter([CastValidator(bound),
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

    @classmethod
    def _annular(cls, takeoffangle_rad, opening_rad):
        elevation_rad = (takeoffangle_rad - opening_rad, takeoffangle_rad + opening_rad)
        azimuth_rad = (0.0, 2.0 * math.pi)
        return elevation_rad, azimuth_rad

    @classmethod
    def annular(cls, takeoffangle_rad, opening_rad):
        elevation_rad, azimuth_rad = cls._annular(takeoffangle_rad, opening_rad)
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

mapper.register(_DelimitedDetector, '{http://pymontecarlo.sf.net}_delimitedDetector',
                ParameterizedElement('elevation_rad', UserType(bound), 'elevation'),
                ParameterizedElement('azimuth_rad', UserType(bound), 'azimuth'))

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

mapper.register(_ChannelsDetector, '{http://pymontecarlo.sf.net}_channelsDetector',
                ParameterizedAttribute('channels', PythonType(int)))

# class _BoundedChannelsDetector(_ChannelsDetector):
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
# #    @classmethod
# #    def __loadxml__(cls, element, *args, **kwargs):
# #        limits = float(element.get('limit_min')), float(element.get('limit_max'))
# #        channels = int(element.get('channels'))
# #
# #        return cls(limits, channels)
# #
# #    def __savexml__(self, element, *args, **kwargs):
# #        limits = self._props['limits']
# #
# #        element.set('limit_min', str(limits[0]))
# #        element.set('limit_max', str(limits[1]))
# #        element.set('channels', str(self.channels))
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

    xlimits = UnitParameter('m', validators=[CastValidator(bound)], doc="Limits in x")
    xbins = Parameter(_bins_validator, "Number of bins in x")
    ylimits = UnitParameter('m', validators=[CastValidator(bound)], doc="Limits in y")
    ybins = Parameter(_bins_validator, "Number of bins in y")
    zlimits = UnitParameter('m', validators=[CastValidator(bound)], doc="Limits in z")
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

mapper.register(_SpatialDetector, '{http://pymontecarlo.sf.net}_spatialDetector',
                ParameterizedElement('xlimits_m', UserType(bound), 'xlimits'),
                ParameterizedAttribute('xbins', PythonType(int)),
                ParameterizedElement('ylimits_m', UserType(bound), 'ylimits'),
                ParameterizedAttribute('ybins', PythonType(int)),
                ParameterizedElement('zlimits_m', UserType(bound), 'zlimits'),
                ParameterizedAttribute('zbins', PythonType(int)))

_energy_limit_validator = \
    SimpleValidator(lambda x: x[0] >= 0 and x[1] >= 0,
                    "Energy must be greater or equal to 0.0")

class _EnergyDetector(_ChannelsDetector):

    limits = UnitParameter('eV',
                           [CastValidator(bound), _energy_limit_validator],
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

mapper.register(_EnergyDetector, '{http://pymontecarlo.sf.net}_energyDetector',
                ParameterizedElement('limits_eV', UserType(bound), 'limits'))

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

mapper.register(_AngularDetector, '{http://pymontecarlo.sf.net}_ngularDetector',
                ParameterizedElement('limits_rad', UserType(bound), 'limits'))

class _PolarAngularDetector(_AngularDetector):

    limits = AngleParameter([CastValidator(bound), _elevation_validator],
                            "Angular limits (in radians)")

    def __init__(self, channels, limits_rad=(-HALFPI, HALFPI)):
        _AngularDetector.__init__(self, channels, limits_rad)

mapper.register(_PolarAngularDetector, '{http://pymontecarlo.sf.net}_polarAngularDetector')

class _AzimuthalAngularDetector(_AngularDetector):

    limits = AngleParameter([CastValidator(bound), _azimuth_validator],
                            "Angular limits (in radians)")

    def __init__(self, channels, limits_rad=(0, TWOPI)):
        _AngularDetector.__init__(self, channels, limits_rad)

mapper.register(_AzimuthalAngularDetector, '{http://pymontecarlo.sf.net}_azimuthalAngularDetector')

class _PhotonDelimitedDetector(_DelimitedDetector):
    pass

mapper.register(_PhotonDelimitedDetector, '{http://pymontecarlo.sf.net}_photonDelimitedDetector')

class BackscatteredElectronEnergyDetector(_EnergyDetector):
    pass

mapper.register(BackscatteredElectronEnergyDetector, '{http://pymontecarlo.sf.net}backscatteredElectronEnergyDetector')

class TransmittedElectronEnergyDetector(_EnergyDetector):
    pass

mapper.register(TransmittedElectronEnergyDetector, '{http://pymontecarlo.sf.net}transmittedElectronEnergyDetector')

class BackscatteredElectronPolarAngularDetector(_PolarAngularDetector):
    pass

mapper.register(BackscatteredElectronPolarAngularDetector, '{http://pymontecarlo.sf.net}backscatteredElectronPolarAngularDetector')

class TransmittedElectronPolarAngularDetector(_PolarAngularDetector):
    pass

mapper.register(TransmittedElectronPolarAngularDetector, '{http://pymontecarlo.sf.net}transmittedElectronPolarAngularDetector')

class BackscatteredElectronAzimuthalAngularDetector(_AzimuthalAngularDetector):
    pass

mapper.register(BackscatteredElectronAzimuthalAngularDetector, '{http://pymontecarlo.sf.net}backscatteredElectronAzimuthalAngularDetector')

class TransmittedElectronAzimuthalAngularDetector(_AzimuthalAngularDetector):
    pass

mapper.register(TransmittedElectronAzimuthalAngularDetector, '{http://pymontecarlo.sf.net}transmittedElectronAzimuthalAngularDetector')

class BackscatteredElectronRadialDetector(_ChannelsDetector):
    pass

mapper.register(BackscatteredElectronRadialDetector, '{http://pymontecarlo.sf.net}backscatteredElectronRadialDetector')

class PhotonPolarAngularDetector(_PolarAngularDetector):
    pass

mapper.register(PhotonPolarAngularDetector, '{http://pymontecarlo.sf.net}photonPolarAngularDetector')

class PhotonAzimuthalAngularDetector(_AzimuthalAngularDetector):
    pass

mapper.register(PhotonAzimuthalAngularDetector, '{http://pymontecarlo.sf.net}photonAzimuthalAngularDetector')

class EnergyDepositedSpatialDetector(_SpatialDetector):
    pass

mapper.register(EnergyDepositedSpatialDetector, '{http://pymontecarlo.sf.net}energyDepositedSpatialDetector')

class PhotonSpectrumDetector(_PhotonDelimitedDetector, _EnergyDetector):

    def __init__(self, elevation_rad, azimuth_rad, limits_eV, channels):
        _PhotonDelimitedDetector.__init__(self, elevation_rad, azimuth_rad)
        _EnergyDetector.__init__(self, limits_eV, channels)

    @classmethod
    def annular(cls, takeoffangle_rad, opening_rad, limits_eV, channels):
        elevation_rad, azimuth_rad = cls._annular(takeoffangle_rad, opening_rad)
        return cls(elevation_rad, azimuth_rad, limits_eV, channels)

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

mapper.register(PhotonSpectrumDetector, '{http://pymontecarlo.sf.net}photonSpectrumDetector')

class PhotonDepthDetector(_PhotonDelimitedDetector, _ChannelsDetector):

    def __init__(self, elevation_rad, azimuth_rad, channels):
        _ChannelsDetector.__init__(self, channels)
        _PhotonDelimitedDetector.__init__(self, elevation_rad, azimuth_rad)

    @classmethod
    def annular(cls, takeoffangle_rad, opening_rad, channels):
        elevation_rad, azimuth_rad = cls._annular(takeoffangle_rad, opening_rad)
        return cls(elevation_rad, azimuth_rad, channels)

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

mapper.register(PhotonDepthDetector, '{http://pymontecarlo.sf.net}photonDepthDetector')

class PhotonRadialDetector(_PhotonDelimitedDetector, _ChannelsDetector):

    def __init__(self, elevation_rad, azimuth_rad, channels):
        _ChannelsDetector.__init__(self, channels)
        _PhotonDelimitedDetector.__init__(self, elevation_rad, azimuth_rad)

    @classmethod
    def annular(cls, takeoffangle_rad, opening_rad, limits_eV, channels):
        elevation_rad, azimuth_rad = cls._annular(takeoffangle_rad, opening_rad)
        return cls(elevation_rad, azimuth_rad, limits_eV, channels)

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

mapper.register(PhotonRadialDetector, '{http://pymontecarlo.sf.net}photonRadialDetector')

class PhotonEmissionMapDetector(_PhotonDelimitedDetector):

    xbins = Parameter(_bins_validator, "Number of bins in x")
    ybins = Parameter(_bins_validator, "Number of bins in y")
    zbins = Parameter(_bins_validator, "Number of bins in z")

    def __init__(self, elevation_rad, azimuth_rad, xbins, ybins, zbins):
        _PhotonDelimitedDetector.__init__(self, elevation_rad, azimuth_rad)

        self.xbins = xbins
        self.ybins = ybins
        self.zbins = zbins

    @classmethod
    def annular(cls, takeoffangle_rad, opening_rad, xbins, ybins, zbins):
        elevation_rad, azimuth_rad = cls._annular(takeoffangle_rad, opening_rad)
        return cls(elevation_rad, azimuth_rad, xbins, ybins, zbins)

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

mapper.register(PhotonEmissionMapDetector, '{http://pymontecarlo.sf.net}photonEmissionMapDetector',
                ParameterizedAttribute('xbins', PythonType(int)),
                ParameterizedAttribute('ybins', PythonType(int)),
                ParameterizedAttribute('zbins', PythonType(int)))

class PhotonIntensityDetector(_PhotonDelimitedDetector):
    pass

mapper.register(PhotonIntensityDetector, '{http://pymontecarlo.sf.net}photonIntensityDetector')

class TimeDetector(_Detector):
    """
    Records simulation time and speed (electron simulated /s).
    """
    pass

mapper.register(TimeDetector, '{http://pymontecarlo.sf.net}timeDetector')

class ElectronFractionDetector(_Detector):
    """
    Records backscattered, transmitted and absorbed fraction of primary electrons.
    """
    pass

mapper.register(ElectronFractionDetector, '{http://pymontecarlo.sf.net}electronFractionDetector')

class ShowersStatisticsDetector(_Detector):
    """
    Records number of simulated particles.
    """
    pass

mapper.register(ShowersStatisticsDetector, '{http://pymontecarlo.sf.net}showersStatisticsDetector')

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

mapper.register(TrajectoryDetector, '{http://pymontecarlo.sf.net}trajectoryDetector',
                ParameterizedAttribute('secondary', PythonType(bool)))

