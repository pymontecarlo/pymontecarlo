#!/usr/bin/env python
"""
================================================================================
:mod:`detector` -- Basic parameters about X-ray and electron detectors
================================================================================

.. module:: detector
   :synopsis: Basic parameters about X-ray and electron detectors

.. inheritance-diagram:: detector

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import math
from xml.etree.ElementTree import Element

# Third party modules.

# Local modules.
from pymontecarlo.util.xmlobj import XMLObject
from pymontecarlo.util.relaxation_data import Transition

# Globals and constants variables.
HALFPI = math.pi / 2.0
TWOPI = math.pi * 2.0
TOLERANCE = 1e-6

class _DelimitedDetector(XMLObject):
    def __init__(self, elevation, azimuth):
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
        
        .. note::
        
           A detector is immutable.
           
        :arg elevation: elevation limits
        :type elevation: :class:`tuple`
        
        :arg azimuth: azimuth limits
        :type azimuth: :class:`tuple`
        """
        XMLObject.__init__(self)

        self.elevation = elevation
        self.azimuth = azimuth

    @classmethod
    def from_xml(cls, element):
        elevation = (float(element.get('elevation_min')),
                     float(element.get('elevation_max')))
        azimuth = (float(element.get('azimuth_min')),
                   float(element.get('azimuth_max')))

        return cls(elevation, azimuth)

    @property
    def elevation(self):
        return self._elevation

    @elevation.setter
    def elevation(self, elevation):
        low, high = elevation

        if abs(low) - HALFPI > TOLERANCE:
            raise ValueError, \
                "Minimum elevation (%s) must be between [-pi/2, pi/2] rad." % low
        if abs(high) - HALFPI > TOLERANCE:
            raise ValueError, \
                "Maximum elevation (%s) must be between [-pi/2, pi/2] rad." % high

        self._elevation = min(low, high), max(low, high)

    @property
    def azimuth(self):
        return self._azimuth

    @azimuth.setter
    def azimuth(self, azimuth):
        low, high = azimuth

        if low < 0 or low > TWOPI + TOLERANCE:
            raise ValueError, \
                "Minimum azimuth (%s) must be between [0, 2pi] rad." % low
        if high < 0 or high > TWOPI + TOLERANCE:
            raise ValueError, \
                "Maximum azimuth (%s) must be between [0, 2pi] rad." % high

        self._azimuth = min(low, high), max(low, high)

    @property
    def solid_angle(self):
        return abs((self.azimuth[1] - self.azimuth[0]) * \
                   (math.cos(self.elevation[0]) - math.cos(self.elevation[1])))

    def to_xml(self):
        element = XMLObject.to_xml(self)

        element.set('elevation_min', str(self.elevation[0]))
        element.set('elevation_max', str(self.elevation[1]))

        element.set('azimuth_min', str(self.azimuth[0]))
        element.set('azimuth_max', str(self.azimuth[1]))

        return element

class _ChannelsDetector(XMLObject):
    def __init__(self, limits, channels, extremums=(float('-inf'), float('inf'))):
        XMLObject.__init__(self)

        self._extremums = extremums
        self.limits = limits
        self.channels = channels

    @classmethod
    def from_xml(cls, element):
        limits = float(element.get('limit_min')), float(element.get('limit_max'))
        channels = int(element.get('channels'))

        return cls(limits, channels)

    @property
    def limits(self):
        return self._limits

    @limits.setter
    def limits(self, limits):
        low, high = limits

        if low < self._extremums[0] - TOLERANCE or low > self._extremums[1] + TOLERANCE:
            raise ValueError, "Lower limit (%s) must be between [%s, %s]." % \
                (low, self._extremums[0], self._extremums[1])
        if high < self._extremums[0] - TOLERANCE or high > self._extremums[1] + TOLERANCE:
            raise ValueError, "Upper limit (%s) must be between [%s, %s]." % \
                (high, self._extremums[0], self._extremums[1])

        self._limits = min(low, high), max(low, high)

    @property
    def channels(self):
        return self._channels

    @channels.setter
    def channels(self, channels):
        if channels < 1:
            raise ValueError, \
                "Number of channels (%s) must be greater or equal to 1." % channels
        self._channels = int(channels)

    def to_xml(self):
        element = XMLObject.to_xml(self)

        element.set('limit_min', str(self.limits[0]))
        element.set('limit_max', str(self.limits[1]))
        element.set('channels', str(self.channels))

        return element

class _SpatialDetector(XMLObject):
    def __init__(self, xlimits, xbins, ylimits, ybins, zlimits, zbins,
                 xextremums=(float('-inf'), float('inf')),
                 yextremums=(float('-inf'), float('inf')),
                 zextremums=(float('-inf'), float('inf'))):
        XMLObject.__init__(self)

        self._xextremums = xextremums
        self._yextremums = yextremums
        self._zextremums = zextremums

        self.xlimits = xlimits
        self.ylimits = ylimits
        self.zlimits = zlimits

        self.xbins = xbins
        self.ybins = ybins
        self.zbins = zbins

    @classmethod
    def from_xml(cls, element):
        xlimits = float(element.get('xlimit_min')), float(element.get('xlimit_max'))
        xbins = int(element.get('xbins'))

        ylimits = float(element.get('ylimit_min')), float(element.get('ylimit_max'))
        ybins = int(element.get('ybins'))

        zlimits = float(element.get('zlimit_min')), float(element.get('zlimit_max'))
        zbins = int(element.get('zbins'))

        return cls(xlimits, xbins, ylimits, ybins, zlimits, zbins)

    @property
    def xlimits(self):
        return self._xlimits

    @xlimits.setter
    def xlimits(self, limits):
        low, high = limits

        if low < self._xextremums[0] or low > self._xextremums[1]:
            raise ValueError, "Lower x limit (%s) must be between [%s, %s]." % \
                (low, self._xextremums[0], self._xextremums[1])
        if high < self._xextremums[0] or high > self._xextremums[1]:
            raise ValueError, "Upper x limit (%s) must be between [%s, %s]." % \
                (high, self._xextremums[0], self._xextremums[1])

        self._xlimits = min(low, high), max(low, high)

    @property
    def ylimits(self):
        return self._ylimits

    @ylimits.setter
    def ylimits(self, limits):
        low, high = limits

        if low < self._yextremums[0] or low > self._yextremums[1]:
            raise ValueError, "Lower y limit (%s) must be between [%s, %s]." % \
                (low, self._yextremums[0], self._yextremums[1])
        if high < self._yextremums[0] or high > self._yextremums[1]:
            raise ValueError, "Upper y limit (%s) must be between [%s, %s]." % \
                (high, self._yextremums[0], self._yextremums[1])

        self._ylimits = min(low, high), max(low, high)

    @property
    def zlimits(self):
        return self._zlimits

    @zlimits.setter
    def zlimits(self, limits):
        low, high = limits

        if low < self._zextremums[0] or low > self._zextremums[1]:
            raise ValueError, "Lower z limit (%s) must be between [%s, %s]." % \
                (low, self._zextremums[0], self._zextremums[1])
        if high < self._zextremums[0] or high > self._zextremums[1]:
            raise ValueError, "Upper z limit (%s) must be between [%s, %s]." % \
                (high, self._zextremums[0], self._zextremums[1])

        self._zlimits = min(low, high), max(low, high)

    @property
    def xbins(self):
        return self._xbins

    @xbins.setter
    def xbins(self, bins):
        if bins < 1:
            raise ValueError, \
                "Number of bins in x (%s) must be greater or equal to 1." % bins
        self._xbins = int(bins)

    @property
    def ybins(self):
        return self._ybins

    @ybins.setter
    def ybins(self, bins):
        if bins < 1:
            raise ValueError, \
                "Number of bins in y (%s) must be greater or equal to 1." % bins
        self._ybins = int(bins)

    @property
    def zbins(self):
        return self._zbins

    @zbins.setter
    def zbins(self, bins):
        if bins < 1:
            raise ValueError, \
                "Number of bins in z (%s) must be greater or equal to 1." % bins
        self._zbins = int(bins)

    def to_xml(self):
        element = XMLObject.to_xml(self)

        element.set('xlimit_min', str(self.xlimits[0]))
        element.set('xlimit_max', str(self.xlimits[1]))
        element.set('xbins', str(self.xbins))

        element.set('ylimit_min', str(self.ylimits[0]))
        element.set('ylimit_max', str(self.ylimits[1]))
        element.set('ybins', str(self.ybins))

        element.set('zlimit_min', str(self.zlimits[0]))
        element.set('zlimit_max', str(self.zlimits[1]))
        element.set('zbins', str(self.zbins))

        return element

class _TransitionDetector(XMLObject):
    def __init__(self, transition):
        XMLObject.__init__(self)

        self.transition = transition

    @classmethod
    def from_xml(cls, element):
        child = list(element.find("transition"))[0]
        material = Transition.from_xml(child)

        return cls(material)

    @property
    def transition(self):
        return self._transition

    @transition.setter
    def transition(self, transition):
        self._transition = transition

    def to_xml(self):
        element = XMLObject.to_xml(self)

        child = Element('transition')
        child.append(self.transition.to_xml())
        element.append(child)

        return element

class _EnergyDetector(_ChannelsDetector):
    def __init__(self, limits, channels):
        _ChannelsDetector.__init__(self, limits, channels, (0.0, float('inf')))

class _RangeDetector(object):
    def _set_range(self, xlow, xhigh, ylow, yhigh, zlow, zhigh):
        raise NotImplementedError

class _ElectronRangeDetector(_RangeDetector):
    pass

class _PhotonRangeDetector(_RangeDetector, _TransitionDetector):
    pass

class _PolarAngularDetector(_ChannelsDetector):
    def __init__(self, channels, limits=(-HALFPI, HALFPI)):
        _ChannelsDetector.__init__(self, limits, channels, (-HALFPI, HALFPI))

    @classmethod
    def from_xml(cls, element):
        # Required due to argument inversion
        det = _ChannelsDetector.from_xml(element)
        return cls(det.channels, det.limits)

class _AzimuthalAngularDetector(_ChannelsDetector):
    def __init__(self, channels, limits=(0, TWOPI)):
        _ChannelsDetector.__init__(self, limits, channels, (0, TWOPI))

    @classmethod
    def from_xml(cls, element):
        # Required due to argument inversion
        det = _ChannelsDetector.from_xml(element)
        return cls(det.channels, det.limits)

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

class PhotonPolarAngularDetector(_PolarAngularDetector):
    pass

class PhotonAzimuthalAngularDetector(_PolarAngularDetector):
    pass

class EnergyDepositedSpatialDetector(_ElectronRangeDetector, _SpatialDetector):
    def __init__(self, xlimits, xbins, ylimits, ybins, zlimits, zbins):
        _ElectronRangeDetector.__init__(self)
        _SpatialDetector.__init__(self, xlimits, xbins,
                                        ylimits, ybins,
                                        zlimits, zbins)

    def _set_range(self, xlow, xhigh, ylow, yhigh, zlow, zhigh):
        self.xlimits = (xlow, xhigh)
        self.ylimits = (ylow, yhigh)
        self.zlimits = (zlow, zhigh)

class PhotonSpectrumDetector(_DelimitedDetector, _EnergyDetector):
    def __init__(self, elevation, azimuth, limits, channels):
        _DelimitedDetector.__init__(self, elevation, azimuth)
        _EnergyDetector.__init__(self, limits, channels)

    @classmethod
    def from_xml(cls, element):
        delimited = _DelimitedDetector.from_xml(element)
        energy = _EnergyDetector.from_xml(element)

        return cls(delimited.elevation, delimited.azimuth,
                   energy.limits, energy.channels)

    def to_xml(self):
        element = XMLObject.to_xml(self)

        element.attrib.update(_DelimitedDetector.to_xml(self).attrib)
        element.attrib.update(_EnergyDetector.to_xml(self).attrib)

        return element

class PhiRhoZDetector(_PhotonRangeDetector, _ChannelsDetector):
    def __init__(self, limits, channels, transition):
        _ChannelsDetector.__init__(self, limits, channels, (float('-inf'), 0))
        _PhotonRangeDetector.__init__(self, transition)

    @classmethod
    def from_xml(cls, element):
        chdet = _ChannelsDetector.from_xml(element)
        rangedet = _PhotonRangeDetector.from_xml(element)

        return cls(chdet.limits, chdet.channels, rangedet.transition)

    def _set_range(self, xlow, xhigh, ylow, yhigh, zlow, zhigh):
        self.limits = (zlow, zhigh)

    def to_xml(self):
        element = XMLObject.to_xml(self)

        element.attrib.update(_ChannelsDetector.to_xml(self).attrib)
        element.append(list(_PhotonRangeDetector.to_xml(self))[0])

        return element

class PhotonIntensityDetector(_TransitionDetector):
    pass

