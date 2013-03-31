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
from pymontecarlo.input.option import Option
from pymontecarlo.util.xmlutil import XMLIO

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

class _DelimitedDetector(Option):
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
        Option.__init__(self)

        self.elevation_rad = elevation_rad
        self.azimuth_rad = azimuth_rad

    def __repr__(self):
        return '<%s(elevation=%s to %s deg, azimuth=%s to %s deg)>' % \
            (self.__class__.__name__,
             self.elevation_deg[0], self.elevation_deg[1],
             self.azimuth_deg[0], self.azimuth_deg[1])

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        elevation = (float(element.get('elevation_min')),
                     float(element.get('elevation_max')))
        azimuth = (float(element.get('azimuth_min')),
                   float(element.get('azimuth_max')))

        return cls(elevation, azimuth)

    def __savexml__(self, element, *args, **kwargs):
        element.set('elevation_min', str(self.elevation_rad[0]))
        element.set('elevation_max', str(self.elevation_rad[1]))

        element.set('azimuth_min', str(self.azimuth_rad[0]))
        element.set('azimuth_max', str(self.azimuth_rad[1]))

    @property
    def elevation_rad(self):
        return self._props['elevation']

    @elevation_rad.setter
    def elevation_rad(self, elevation):
        low, high = elevation

        if abs(low) - HALFPI > TOLERANCE:
            raise ValueError, \
                "Minimum elevation (%s) must be between [-pi/2, pi/2] rad." % low
        if abs(high) - HALFPI > TOLERANCE:
            raise ValueError, \
                "Maximum elevation (%s) must be between [-pi/2, pi/2] rad." % high
        if abs(high - low) <= TOLERANCE:
            raise ValueError, "Elevations (%s and %s) are equal " % (low, high)

        self._props['elevation'] = min(low, high), max(low, high)

    @property
    def elevation_deg(self):
        return tuple(map(math.degrees, self.elevation_rad))

    @elevation_deg.setter
    def elevation_deg(self, elevation):
        self.elevation_rad = map(math.radians, elevation)

    @property
    def azimuth_rad(self):
        return self._props['azimuth']

    @azimuth_rad.setter
    def azimuth_rad(self, azimuth):
        low, high = azimuth

        if low < 0 or low > TWOPI + TOLERANCE:
            raise ValueError, \
                "Minimum azimuth (%s) must be between [0, 2pi] rad." % low
        if high < 0 or high > TWOPI + TOLERANCE:
            raise ValueError, \
                "Maximum azimuth (%s) must be between [0, 2pi] rad." % high
        if abs(high - low) <= TOLERANCE:
            raise ValueError, "Azimuths (%s and %s) are equal " % (low, high)

        self._props['azimuth'] = min(low, high), max(low, high)

    @property
    def azimuth_deg(self):
        return tuple(map(math.degrees, self.azimuth_rad))

    @azimuth_deg.setter
    def azimuth_deg(self, azimuth):
        self.azimuth_rad = map(math.radians, azimuth)

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

class _ChannelsDetector(Option):
    def __init__(self, channels):
        Option.__init__(self)
        self.channels = channels

    def __repr__(self):
        return '<%s(channels=%s)>' % (self.__class__.__name__, self.channels)

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        channels = int(element.get('channels'))
        return cls(channels)

    def __savexml__(self, element, *args, **kwargs):
        element.set('channels', str(self.channels))

    @property
    def channels(self):
        return self._props['channels']

    @channels.setter
    def channels(self, channels):
        if channels < 1:
            raise ValueError, \
                "Number of channels (%s) must be greater or equal to 1." % channels
        self._props['channels'] = int(channels)

class _DelimitedChannelsDetector(_ChannelsDetector):

    def __init__(self, extremums=(float('-inf'), float('inf'))):
        _ChannelsDetector.__init__(self, 1)
        self._extremums = extremums

    def __repr__(self):
        limits = self._props['limits']
        return '<%s(limits=%s to %s, channels=%s)>' % \
            (self.__class__.__name__, limits[0], limits[1], self.channels)

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        limits = float(element.get('limit_min')), float(element.get('limit_max'))
        channels = int(element.get('channels'))

        return cls(limits, channels)

    def __savexml__(self, element, *args, **kwargs):
        limits = self._props['limits']

        element.set('limit_min', str(limits[0]))
        element.set('limit_max', str(limits[1]))
        element.set('channels', str(self.channels))

    def _set_limits(self, limits):
        low, high = limits

        if low < self._extremums[0] - TOLERANCE or low > self._extremums[1] + TOLERANCE:
            raise ValueError, "Lower limit (%s) must be between [%s, %s]." % \
                (low, self._extremums[0], self._extremums[1])
        if high < self._extremums[0] - TOLERANCE or high > self._extremums[1] + TOLERANCE:
            raise ValueError, "Upper limit (%s) must be between [%s, %s]." % \
                (high, self._extremums[0], self._extremums[1])

        self._props['limits'] = min(low, high), max(low, high)

class _SpatialDetector(Option):
    def __init__(self, xlimits_m, xbins, ylimits_m, ybins, zlimits_m, zbins,
                 xextremums=(float('-inf'), float('inf')),
                 yextremums=(float('-inf'), float('inf')),
                 zextremums=(float('-inf'), float('inf'))):
        Option.__init__(self)

        self._xextremums = xextremums
        self._yextremums = yextremums
        self._zextremums = zextremums

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

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        xlimits = float(element.get('xlimit_min')), float(element.get('xlimit_max'))
        xbins = int(element.get('xbins'))

        ylimits = float(element.get('ylimit_min')), float(element.get('ylimit_max'))
        ybins = int(element.get('ybins'))

        zlimits = float(element.get('zlimit_min')), float(element.get('zlimit_max'))
        zbins = int(element.get('zbins'))

        return cls(xlimits, xbins, ylimits, ybins, zlimits, zbins)

    def __savexml__(self, element, *args, **kwargs):
        element.set('xlimit_min', str(self.xlimits_m[0]))
        element.set('xlimit_max', str(self.xlimits_m[1]))
        element.set('xbins', str(self.xbins))

        element.set('ylimit_min', str(self.ylimits_m[0]))
        element.set('ylimit_max', str(self.ylimits_m[1]))
        element.set('ybins', str(self.ybins))

        element.set('zlimit_min', str(self.zlimits_m[0]))
        element.set('zlimit_max', str(self.zlimits_m[1]))
        element.set('zbins', str(self.zbins))

    @property
    def xlimits_m(self):
        return self._props['xlimits']

    @xlimits_m.setter
    def xlimits_m(self, limits):
        low, high = limits

        if low < self._xextremums[0] or low > self._xextremums[1]:
            raise ValueError, "Lower x limit (%s) must be between [%s, %s]." % \
                (low, self._xextremums[0], self._xextremums[1])
        if high < self._xextremums[0] or high > self._xextremums[1]:
            raise ValueError, "Upper x limit (%s) must be between [%s, %s]." % \
                (high, self._xextremums[0], self._xextremums[1])

        self._props['xlimits'] = min(low, high), max(low, high)

    @property
    def ylimits_m(self):
        return self._props['ylimits']

    @ylimits_m.setter
    def ylimits_m(self, limits):
        low, high = limits

        if low < self._yextremums[0] or low > self._yextremums[1]:
            raise ValueError, "Lower y limit (%s) must be between [%s, %s]." % \
                (low, self._yextremums[0], self._yextremums[1])
        if high < self._yextremums[0] or high > self._yextremums[1]:
            raise ValueError, "Upper y limit (%s) must be between [%s, %s]." % \
                (high, self._yextremums[0], self._yextremums[1])

        self._props['ylimits'] = min(low, high), max(low, high)

    @property
    def zlimits_m(self):
        return self._props['zlimits']

    @zlimits_m.setter
    def zlimits_m(self, limits):
        low, high = limits

        if low < self._zextremums[0] or low > self._zextremums[1]:
            raise ValueError, "Lower z limit (%s) must be between [%s, %s]." % \
                (low, self._zextremums[0], self._zextremums[1])
        if high < self._zextremums[0] or high > self._zextremums[1]:
            raise ValueError, "Upper z limit (%s) must be between [%s, %s]." % \
                (high, self._zextremums[0], self._zextremums[1])

        self._props['zlimits'] = min(low, high), max(low, high)

    @property
    def xbins(self):
        return self._props['xbins']

    @xbins.setter
    def xbins(self, bins):
        if bins < 1:
            raise ValueError, \
                "Number of bins in x (%s) must be greater or equal to 1." % bins
        self._props['xbins'] = int(bins)

    @property
    def ybins(self):
        return self._props['ybins']

    @ybins.setter
    def ybins(self, bins):
        if bins < 1:
            raise ValueError, \
                "Number of bins in y (%s) must be greater or equal to 1." % bins
        self._props['ybins'] = int(bins)

    @property
    def zbins(self):
        return self._props['zbins']

    @zbins.setter
    def zbins(self, bins):
        if bins < 1:
            raise ValueError, \
                "Number of bins in z (%s) must be greater or equal to 1." % bins
        self._props['zbins'] = int(bins)

class _EnergyDetector(_DelimitedChannelsDetector):
    def __init__(self, limits_eV, channels):
        _DelimitedChannelsDetector.__init__(self, (0.0, float('inf')))

        self.limits_eV = limits_eV
        self.channels = channels

    def __repr__(self):
        return "<%s(limits=%s to %s eV, channels=%s)>" % \
            (self.__class__.__name__, self.limits_eV[0], self.limits_eV[1], self.channels)

    @property
    def limits_eV(self):
        return self._props['limits']

    @limits_eV.setter
    def limits_eV(self, limits):
        self._set_limits(limits)

class _RangeDetector(object):
    def _set_range(self, xlow_m, xhigh_m, ylow_m, yhigh_m, zlow_m, zhigh_m):
        raise NotImplementedError

class _ElectronRangeDetector(_RangeDetector):
    pass

class _PhotonRangeDetector(_RangeDetector):
    pass

class _AngularDetector(_DelimitedChannelsDetector):
    def __init__(self, channels, limits_rad, extremums):
        _DelimitedChannelsDetector.__init__(self, extremums)

        self.limits_rad = limits_rad
        self.channels = channels

    def __repr__(self):
        return "<%s(limits=%s to %s rad, channels=%s)>" % \
            (self.__class__.__name__, self.limits_rad[0], self.limits_rad[1], self.channels)

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        # Required due to argument inversion
        limits = float(element.get('limit_min')), float(element.get('limit_max'))
        channels = int(element.get('channels'))

        return cls(channels, limits)

    @property
    def limits_rad(self):
        return self._props['limits']

    @limits_rad.setter
    def limits_rad(self, limits):
        self._set_limits(limits)

class _PolarAngularDetector(_AngularDetector):
    def __init__(self, channels, limits_rad=(-HALFPI, HALFPI)):
        _AngularDetector.__init__(self, channels, limits_rad,
                                  extremums=(-HALFPI, HALFPI))

class _AzimuthalAngularDetector(_AngularDetector):
    def __init__(self, channels, limits_rad=(0, TWOPI)):
        _AngularDetector.__init__(self, channels, limits_rad,
                                  extremums=(0, TWOPI))

class _PhotonDelimitedDetector(_DelimitedDetector):
    pass

class BackscatteredElectronEnergyDetector(_EnergyDetector):
    pass

XMLIO.register('{http://pymontecarlo.sf.net}backscatteredElectronEnergyDetector', BackscatteredElectronEnergyDetector)

class TransmittedElectronEnergyDetector(_EnergyDetector):
    pass

XMLIO.register('{http://pymontecarlo.sf.net}transmittedElectronEnergyDetector', TransmittedElectronEnergyDetector)

class BackscatteredElectronPolarAngularDetector(_PolarAngularDetector):
    pass

XMLIO.register('{http://pymontecarlo.sf.net}backscatteredElectronPolarAngularDetector', BackscatteredElectronPolarAngularDetector)

class TransmittedElectronPolarAngularDetector(_PolarAngularDetector):
    pass

XMLIO.register('{http://pymontecarlo.sf.net}transmittedElectronPolarAngularDetector', TransmittedElectronPolarAngularDetector)

class BackscatteredElectronAzimuthalAngularDetector(_AzimuthalAngularDetector):
    pass

XMLIO.register('{http://pymontecarlo.sf.net}backscatteredElectronAzimuthalAngularDetector', BackscatteredElectronAzimuthalAngularDetector)

class TransmittedElectronAzimuthalAngularDetector(_AzimuthalAngularDetector):
    pass

XMLIO.register('{http://pymontecarlo.sf.net}transmittedElectronAzimuthalAngularDetector', TransmittedElectronAzimuthalAngularDetector)

class BackscatteredElectronRadialDetector(_ChannelsDetector):
    pass

XMLIO.register('{http://pymontecarlo.sf.net}backscatteredElectronRadialDetector', BackscatteredElectronRadialDetector)

class PhotonPolarAngularDetector(_PolarAngularDetector):
    pass

XMLIO.register('{http://pymontecarlo.sf.net}photonPolarAngularDetector', PhotonPolarAngularDetector)

class PhotonAzimuthalAngularDetector(_AzimuthalAngularDetector):
    pass

XMLIO.register('{http://pymontecarlo.sf.net}photonAzimuthalAngularDetector', PhotonAzimuthalAngularDetector)

class EnergyDepositedSpatialDetector(_ElectronRangeDetector, _SpatialDetector):
    def __init__(self, xlimits_m, xbins, ylimits_m, ybins, zlimits_m, zbins):
        _ElectronRangeDetector.__init__(self)
        _SpatialDetector.__init__(self, xlimits_m, xbins,
                                        ylimits_m, ybins,
                                        zlimits_m, zbins)

    def _set_range(self, xlow_m, xhigh_m, ylow_m, yhigh_m, zlow_m, zhigh_m):
        self.xlimits_m = (xlow_m, xhigh_m)
        self.ylimits_m = (ylow_m, yhigh_m)
        self.zlimits_m = (zlow_m, zhigh_m)

XMLIO.register('{http://pymontecarlo.sf.net}energyDepositedSpatialDetector', EnergyDepositedSpatialDetector)

class PhotonSpectrumDetector(_PhotonDelimitedDetector, _EnergyDetector):
    def __init__(self, elevation_rad, azimuth_rad, limits_eV, channels):
        _PhotonDelimitedDetector.__init__(self, elevation_rad, azimuth_rad)
        _EnergyDetector.__init__(self, limits_eV, channels)

    def __repr__(self):
        return "<%s(elevation=%s to %s rad, azimuth=%s to %s rad, limits=%s to %s eV, channels=%s)>" % \
            (self.__class__.__name__,
             self.elevation_rad[0], self.elevation_rad[1],
             self.azimuth_rad[0], self.azimuth_rad[1],
             self.limits_eV[0], self.limits_eV[1],
             self.channels)

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        delimited = _PhotonDelimitedDetector.__loadxml__(element, *args, **kwargs)
        energy = _EnergyDetector.__loadxml__(element, *args, **kwargs)

        return cls(delimited.elevation_rad, delimited.azimuth_rad,
                   energy.limits_eV, energy.channels)

    def __savexml__(self, element, *args, **kwargs):
        _PhotonDelimitedDetector.__savexml__(self, element, *args, **kwargs)
        _EnergyDetector.__savexml__(self, element, *args, **kwargs)

XMLIO.register('{http://pymontecarlo.sf.net}photonSpectrumDetector', PhotonSpectrumDetector)

class PhotonDepthDetector(_PhotonDelimitedDetector, _ChannelsDetector):
    def __init__(self, elevation_rad, azimuth_rad, channels):
        _ChannelsDetector.__init__(self, channels)
        _PhotonDelimitedDetector.__init__(self, elevation_rad, azimuth_rad)

    def __repr__(self):
        return '<%s(elevation=%s to %s rad, azimuth=%s to %s rad, channels=%s)>' % \
            (self.__class__.__name__,
             self.elevation_rad[0], self.elevation_rad[1],
             self.azimuth_rad[0], self.azimuth_rad[1],
             self.channels)

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        delimited = _PhotonDelimitedDetector.__loadxml__(element, *args, **kwargs)
        channels = _ChannelsDetector.__loadxml__(element, *args, **kwargs)
        return cls(delimited.elevation_rad, delimited.azimuth_rad, channels.channels)

    def __savexml__(self, element, *args, **kwargs):
        _PhotonDelimitedDetector.__savexml__(self, element, *args, **kwargs)
        _ChannelsDetector.__savexml__(self, element, *args, **kwargs)

XMLIO.register('{http://pymontecarlo.sf.net}photonDepthDetector', PhotonDepthDetector)

class PhotonRadialDetector(_PhotonDelimitedDetector, _ChannelsDetector):
    def __init__(self, elevation_rad, azimuth_rad, channels):
        _ChannelsDetector.__init__(self, channels)
        _PhotonDelimitedDetector.__init__(self, elevation_rad, azimuth_rad)

    def __repr__(self):
        return '<%s(elevation=%s to %s rad, azimuth=%s to %s rad, channels=%s)>' % \
            (self.__class__.__name__,
             self.elevation_rad[0], self.elevation_rad[1],
             self.azimuth_rad[0], self.azimuth_rad[1],
             self.channels)

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        delimited = _PhotonDelimitedDetector.__loadxml__(element, *args, **kwargs)
        channels = _ChannelsDetector.__loadxml__(element, *args, **kwargs)
        return cls(delimited.elevation_rad, delimited.azimuth_rad, channels.channels)

    def __savexml__(self, element, *args, **kwargs):
        _PhotonDelimitedDetector.__savexml__(self, element, *args, **kwargs)
        _ChannelsDetector.__savexml__(self, element, *args, **kwargs)

XMLIO.register('{http://pymontecarlo.sf.net}photonRadialDetector', PhotonRadialDetector)

class PhotonEmissionMapDetector(_PhotonDelimitedDetector):
    def __init__(self, elevation_rad, azimuth_rad, xbins, ybins, zbins):
        _PhotonDelimitedDetector.__init__(self, elevation_rad, azimuth_rad)

        self.xbins = xbins
        self.ybins = ybins
        self.zbins = zbins

    def __repr__(self):
        return '<%s(elevation=%s to %s rad, azimuth=%s to %s rad, bins=(%s, %s, %s))>' % \
            (self.__class__.__name__,
             self.elevation_rad[0], self.elevation_rad[1],
             self.azimuth_rad[0], self.azimuth_rad[1],
             self.xbins, self.ybins, self.zbins)

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        delimited = _PhotonDelimitedDetector.__loadxml__(element, *args, **kwargs)
        xbins = int(element.get('xbins'))
        ybins = int(element.get('ybins'))
        zbins = int(element.get('zbins'))
        return cls(delimited.elevation_rad, delimited.azimuth_rad,
                   xbins, ybins, zbins)

    def __savexml__(self, element, *args, **kwargs):
        _PhotonDelimitedDetector.__savexml__(self, element, *args, **kwargs)
        element.set('xbins', str(self.xbins))
        element.set('ybins', str(self.ybins))
        element.set('zbins', str(self.zbins))

    @property
    def xbins(self):
        return self._props['xbins']

    @xbins.setter
    def xbins(self, bins):
        if bins < 1:
            raise ValueError, \
                "Number of bins (%s) must be greater or equal to 1." % bins
        self._props['xbins'] = int(bins)

    @property
    def ybins(self):
        return self._props['ybins']

    @ybins.setter
    def ybins(self, bins):
        if bins < 1:
            raise ValueError, \
                "Number of bins (%s) must be greater or equal to 1." % bins
        self._props['ybins'] = int(bins)

    @property
    def zbins(self):
        return self._props['zbins']

    @zbins.setter
    def zbins(self, bins):
        if bins < 1:
            raise ValueError, \
                "Number of bins (%s) must be greater or equal to 1." % bins
        self._props['zbins'] = int(bins)

XMLIO.register('{http://pymontecarlo.sf.net}photonEmissionMapDetector', PhotonEmissionMapDetector)

class PhotonIntensityDetector(_PhotonDelimitedDetector):
    pass

XMLIO.register('{http://pymontecarlo.sf.net}photonIntensityDetector', PhotonIntensityDetector)

class TimeDetector(Option):
    """
    Records simulation time and speed (electron simulated /s).
    """
    pass

XMLIO.register('{http://pymontecarlo.sf.net}timeDetector', TimeDetector)

class ElectronFractionDetector(Option):
    """
    Records backscattered, transmitted and absorbed fraction of primary electrons.
    """
    pass

XMLIO.register('{http://pymontecarlo.sf.net}electronFractionDetector', ElectronFractionDetector)

class ShowersStatisticsDetector(Option):
    """
    Records number of simulated particles.
    """
    pass

XMLIO.register('{http://pymontecarlo.sf.net}showersStatisticsDetector', ShowersStatisticsDetector)

class TrajectoryDetector(Option):
    """
    Records the trajectories of particles.
    """

    def __init__(self, secondary=True):
        """
        Creates a detector of trajectories.
        
        .. note::
        
           The number of trajectories is defined by the :class:`ShowerLimit`
        
        :arg secondary: whether to simulate secondary particles
        :type secondary: :class:`bool`
        """
        Option.__init__(self)
        self.secondary = secondary

    def __repr__(self):
        prep = 'with' if self.secondary else 'without'
        return '<%s(%s secondary particles)>' % (self.__class__.__name__, prep)

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        secondary = True if element.get('secondary') == 'true' else False

        return cls(secondary)

    def __savexml__(self, element, *args, **kwargs):
        element.set('secondary', str(self.secondary).lower())

    @property
    def secondary(self):
        """
        Whether to simulate secondary particles.
        """
        return self._props['secondary']

    @secondary.setter
    def secondary(self, secondary):
        self._props['secondary'] = secondary

XMLIO.register('{http://pymontecarlo.sf.net}trajectoryDetector', TrajectoryDetector)

