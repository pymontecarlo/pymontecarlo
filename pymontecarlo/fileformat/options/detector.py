#!/usr/bin/env python
"""
================================================================================
:mod:`detector` -- XML handlers for detectors
================================================================================

.. module:: detector
   :synopsis: XML handlers for detectors

.. inheritance-diagram:: pymontecarlo.fileformat.options.detector

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import xml.etree.ElementTree as etree

# Third party modules.
from pyxray.transition import Transition

# Local modules.
from pymontecarlo.fileformat.xmlhandler import _XMLHandler

from pymontecarlo.options.detector import \
    (_DelimitedDetector, _ChannelsDetector, _SpatialDetector, _EnergyDetector,
     _AngularDetector, _PolarAngularDetector, _AzimuthalAngularDetector,
     _TransitionsDetector,
     BackscatteredElectronEnergyDetector, TransmittedElectronEnergyDetector,
     BackscatteredElectronPolarAngularDetector, TransmittedElectronPolarAngularDetector,
     BackscatteredElectronAzimuthalAngularDetector, TransmittedElectronAzimuthalAngularDetector,
     BackscatteredElectronRadialDetector,
     PhotonSpectrumDetector, PhotonDepthDetector, PhiZDetector,
     PhotonRadialDetector, PhotonEmissionMapDetector, PhotonIntensityDetector,
     TimeDetector, ElectronFractionDetector, ShowersStatisticsDetector,
     TrajectoryDetector)

# Globals and constants variables.

class _DelimitedDetectorXMLHandler(_XMLHandler):

    TAG = '{http://pymontecarlo.sf.net}_delimitedDetector'
    CLASS = _DelimitedDetector

    def parse(self, element):
        subelement = element.find('elevation')
        if subelement is None:
            raise ValueError("Element 'elevation' not found")
        elevation_lower = self._parse_numerical_parameter(subelement, 'lower')
        elevation_upper = self._parse_numerical_parameter(subelement, 'upper')
        elevation_rad = list(zip(elevation_lower, elevation_upper))

        subelement = element.find('azimuth')
        if subelement is None:
            raise ValueError("Element 'azimuth' not found")
        azimuth_lower = self._parse_numerical_parameter(subelement, 'lower')
        azimuth_upper = self._parse_numerical_parameter(subelement, 'upper')
        azimuth_rad = list(zip(azimuth_lower, azimuth_upper))

        return _DelimitedDetector(elevation_rad, azimuth_rad)

    def convert(self, obj):
        element = _XMLHandler.convert(self, obj)

        subelement = etree.SubElement(element, 'elevation')
        self._convert_numerical_parameter(subelement, obj.elevation_rad.lower, 'lower')
        self._convert_numerical_parameter(subelement, obj.elevation_rad.upper, 'upper')

        subelement = etree.SubElement(element, 'azimuth')
        self._convert_numerical_parameter(subelement, obj.azimuth_rad.lower, 'lower')
        self._convert_numerical_parameter(subelement, obj.azimuth_rad.upper, 'upper')

        return element

class _ChannelsDetectorXMLHandler(_XMLHandler):

    TAG = '{http://pymontecarlo.sf.net}_channelsDetector'
    CLASS = _ChannelsDetector

    def parse(self, element):
        subelement = element.find('channels')
        if subelement is None:
            raise ValueError("Element 'channels' not found")
        channels = self._parse_numerical_parameter(subelement)

        return _ChannelsDetector(channels)

    def convert(self, obj):
        element = _XMLHandler.convert(self, obj)

        subelement = etree.SubElement(element, 'channels')
        self._convert_numerical_parameter(subelement, obj.channels)

        return element

class _SpatialDetectorXMLHandler(_XMLHandler):

    TAG = '{http://pymontecarlo.sf.net}_spatialDetector'
    CLASS = _SpatialDetector

    def parse(self, element):
        subelement = element.find('xlimits')
        if subelement is None:
            raise ValueError("Element 'xlimits' not found")
        xlimit_lower = self._parse_numerical_parameter(subelement, 'lower')
        xlimit_upper = self._parse_numerical_parameter(subelement, 'upper')
        xlimits_m = list(zip(xlimit_lower, xlimit_upper))

        subelement = element.find('xbins')
        if subelement is None:
            raise ValueError("Element 'xbins' not found")
        xbins = self._parse_numerical_parameter(subelement)

        subelement = element.find('ylimits')
        if subelement is None:
            raise ValueError("Element 'ylimits' not found")
        ylimit_lower = self._parse_numerical_parameter(subelement, 'lower')
        ylimit_upper = self._parse_numerical_parameter(subelement, 'upper')
        ylimits_m = list(zip(ylimit_lower, ylimit_upper))

        subelement = element.find('ybins')
        if subelement is None:
            raise ValueError("Element 'ybins' not found")
        ybins = self._parse_numerical_parameter(subelement)

        subelement = element.find('zlimits')
        if subelement is None:
            raise ValueError("Element 'zlimits' not found")
        zlimit_lower = self._parse_numerical_parameter(subelement, 'lower')
        zlimit_upper = self._parse_numerical_parameter(subelement, 'upper')
        zlimits_m = list(zip(zlimit_lower, zlimit_upper))

        subelement = element.find('zbins')
        if subelement is None:
            raise ValueError("Element 'zbins' not found")
        zbins = self._parse_numerical_parameter(subelement)

        return _SpatialDetector(xlimits_m, xbins, ylimits_m, ybins, zlimits_m, zbins)

    def convert(self, obj):
        element = _XMLHandler.convert(self, obj)

        subelement = etree.SubElement(element, 'xlimits')
        self._convert_numerical_parameter(subelement, obj.xlimits_m.lower, 'lower')
        self._convert_numerical_parameter(subelement, obj.xlimits_m.upper, 'upper')

        subelement = etree.SubElement(element, 'xbins')
        self._convert_numerical_parameter(subelement, obj.xbins)

        subelement = etree.SubElement(element, 'ylimits')
        self._convert_numerical_parameter(subelement, obj.ylimits_m.lower, 'lower')
        self._convert_numerical_parameter(subelement, obj.ylimits_m.upper, 'upper')

        subelement = etree.SubElement(element, 'ybins')
        self._convert_numerical_parameter(subelement, obj.ybins)

        subelement = etree.SubElement(element, 'zlimits')
        self._convert_numerical_parameter(subelement, obj.zlimits_m.lower, 'lower')
        self._convert_numerical_parameter(subelement, obj.zlimits_m.upper, 'upper')

        subelement = etree.SubElement(element, 'zbins')
        self._convert_numerical_parameter(subelement, obj.zbins)

        return element

class _EnergyDetectorXMLHandler(_ChannelsDetectorXMLHandler):

    TAG = '{http://pymontecarlo.sf.net}_energyDetector'
    CLASS = _EnergyDetector

    def parse(self, element):
        det = _ChannelsDetectorXMLHandler.parse(self, element)

        subelement = element.find('limits')
        if subelement is None:
            raise ValueError("Element 'limits' not found")
        limit_lower = self._parse_numerical_parameter(subelement, 'lower')
        limit_upper = self._parse_numerical_parameter(subelement, 'upper')
        limits_eV = list(zip(limit_lower, limit_upper))

        return _EnergyDetector(det.channels, limits_eV)

    def convert(self, obj):
        element = _ChannelsDetectorXMLHandler.convert(self, obj)

        subelement = etree.SubElement(element, 'limits')
        self._convert_numerical_parameter(subelement, obj.limits_eV.lower, 'lower')
        self._convert_numerical_parameter(subelement, obj.limits_eV.upper, 'upper')

        return element

class _AngularDetectorXMLHandler(_ChannelsDetectorXMLHandler):

    def parse(self, element):
        det = _ChannelsDetectorXMLHandler.parse(self, element)

        subelement = element.find('limits')
        if subelement is None:
            raise ValueError("Element 'limits' not found")
        limit_lower = self._parse_numerical_parameter(subelement, 'lower')
        limit_upper = self._parse_numerical_parameter(subelement, 'upper')
        limits_rad = list(zip(limit_lower, limit_upper))

        return _AngularDetector(det.channels, limits_rad)

    def convert(self, obj):
        element = _ChannelsDetectorXMLHandler.convert(self, obj)

        subelement = etree.SubElement(element, 'limits')
        self._convert_numerical_parameter(subelement, obj.limits_rad.lower, 'lower')
        self._convert_numerical_parameter(subelement, obj.limits_rad.upper, 'upper')

        return element

class _PolarAngularDetectorXMLHandler(_AngularDetectorXMLHandler):

    TAG = '{http://pymontecarlo.sf.net}_polarAngularDetector'
    CLASS = _PolarAngularDetector

    def parse(self, element):
        det = _AngularDetectorXMLHandler.parse(self, element)
        return _PolarAngularDetector(det.channels, det.limits_rad)

class _AzimuthalAngularDetectorXMLHandler(_AngularDetectorXMLHandler):

    TAG = '{http://pymontecarlo.sf.net}_azimuthalAngularDetector'
    CLASS = _AzimuthalAngularDetector

    def parse(self, element):
        det = _AngularDetectorXMLHandler.parse(self, element)
        return _AzimuthalAngularDetector(det.channels, det.limits_rad)

class _TransitionsDetectorXMLHandler(_XMLHandler):

    TAG = '{http://pymontecarlo.sf.net}_transitionsDetector'
    CLASS = _TransitionsDetector

    def parse(self, element):
        transitions = []

        subelement = element.find('transitions')
        if subelement is not None:
            for subsubelement in subelement:
                z = int(self._parse_numerical_parameter(subsubelement, 'z'))
                src = int(self._parse_numerical_parameter(subsubelement, 'src'))
                dest = int(self._parse_numerical_parameter(subsubelement, 'dest'))
                transitions.append(Transition(z, src, dest))

        return _TransitionsDetector(transitions)

    def convert(self, obj):
        element = _XMLHandler.convert(self, obj)

        subelement = etree.SubElement(element, 'transitions')
        for transition in obj.transitions:
            subsubelement = etree.SubElement(subelement, 'transition')
            subsubelement.set('z', str(transition.z))
            subsubelement.set('src', str(transition.src.index))
            subsubelement.set('dest', str(transition.dest.index))

        return element

class BackscatteredElectronEnergyDetectorXMLHandler(_EnergyDetectorXMLHandler):

    TAG = '{http://pymontecarlo.sf.net}backscatteredElectronEnergyDetector'
    CLASS = BackscatteredElectronEnergyDetector

    def parse(self, element):
        det = _EnergyDetectorXMLHandler.parse(self, element)
        return BackscatteredElectronEnergyDetector(det.channels, det.limits_eV)

class TransmittedElectronEnergyDetectorXMLHandler(_EnergyDetectorXMLHandler):

    TAG = '{http://pymontecarlo.sf.net}transmittedElectronEnergyDetector'
    CLASS = TransmittedElectronEnergyDetector

    def parse(self, element):
        det = _EnergyDetectorXMLHandler.parse(self, element)
        return TransmittedElectronEnergyDetector(det.channels, det.limits_eV)

class BackscatteredElectronPolarAngularDetectorXMLHandler(_PolarAngularDetectorXMLHandler):

    TAG = '{http://pymontecarlo.sf.net}backscatteredElectronPolarAngularDetector'
    CLASS = BackscatteredElectronPolarAngularDetector

    def parse(self, element):
        det = _PolarAngularDetectorXMLHandler.parse(self, element)
        return BackscatteredElectronPolarAngularDetector(det.channels, det.limits_rad)

class TransmittedElectronPolarAngularDetectorXMLHandler(_PolarAngularDetectorXMLHandler):

    TAG = '{http://pymontecarlo.sf.net}transmittedElectronPolarAngularDetector'
    CLASS = TransmittedElectronPolarAngularDetector

    def parse(self, element):
        det = _PolarAngularDetectorXMLHandler.parse(self, element)
        return TransmittedElectronPolarAngularDetector(det.channels, det.limits_rad)

class BackscatteredElectronAzimuthalAngularDetectorXMLHandler(_AzimuthalAngularDetectorXMLHandler):

    TAG = '{http://pymontecarlo.sf.net}backscatteredElectronAzimuthalAngularDetector'
    CLASS = BackscatteredElectronAzimuthalAngularDetector

    def parse(self, element):
        det = _AzimuthalAngularDetectorXMLHandler.parse(self, element)
        return BackscatteredElectronAzimuthalAngularDetector(det.channels, det.limits_rad)

class TransmittedElectronAzimuthalAngularDetectorXMLHandler(_AzimuthalAngularDetectorXMLHandler):

    TAG = '{http://pymontecarlo.sf.net}transmittedElectronAzimuthalAngularDetector'
    CLASS = TransmittedElectronAzimuthalAngularDetector

    def parse(self, element):
        det = _AzimuthalAngularDetectorXMLHandler.parse(self, element)
        return TransmittedElectronAzimuthalAngularDetector(det.channels, det.limits_rad)

class BackscatteredElectronRadialDetectorXMLHandler(_ChannelsDetectorXMLHandler):

    TAG = '{http://pymontecarlo.sf.net}backscatteredElectronRadialDetector'
    CLASS = BackscatteredElectronRadialDetector

    def parse(self, element):
        det = _ChannelsDetectorXMLHandler.parse(self, element)
        return BackscatteredElectronRadialDetector(det.channels)

class PhotonSpectrumDetectorXMLHandler(_DelimitedDetectorXMLHandler,
                                       _EnergyDetectorXMLHandler):

    TAG = '{http://pymontecarlo.sf.net}photonSpectrumDetector'
    CLASS = PhotonSpectrumDetector

    def parse(self, element):
        det1 = _DelimitedDetectorXMLHandler.parse(self, element)
        det2 = _EnergyDetectorXMLHandler.parse(self, element)
        return PhotonSpectrumDetector(det1.elevation_rad, det1.azimuth_rad,
                                      det2.channels, det2.limits_eV)

    def convert(self, obj):
        element1 = _DelimitedDetectorXMLHandler.convert(self, obj)
        element2 = _EnergyDetectorXMLHandler.convert(self, obj)
        element1.extend(element2)
        return element1

class PhotonDepthDetectorXMLHandler(_DelimitedDetectorXMLHandler,
                                    _ChannelsDetectorXMLHandler,
                                    _TransitionsDetectorXMLHandler):

    TAG = '{http://pymontecarlo.sf.net}photonDepthDetector'
    CLASS = PhotonDepthDetector

    def parse(self, element):
        det1 = _DelimitedDetectorXMLHandler.parse(self, element)
        det2 = _ChannelsDetectorXMLHandler.parse(self, element)
        det3 = _TransitionsDetectorXMLHandler.parse(self, element)
        return PhotonDepthDetector(det1.elevation_rad, det1.azimuth_rad,
                                   det2.channels, det3.transitions)

    def convert(self, obj):
        element1 = _DelimitedDetectorXMLHandler.convert(self, obj)
        element2 = _ChannelsDetectorXMLHandler.convert(self, obj)
        element1.extend(element2)
        element3 = _TransitionsDetectorXMLHandler.convert(self, obj)
        element1.extend(element3)
        return element1

class PhiZDetectorXMLHandler(_DelimitedDetectorXMLHandler,
                             _ChannelsDetectorXMLHandler,
                             _TransitionsDetectorXMLHandler):

    TAG = '{http://pymontecarlo.sf.net}phiZDetector'
    CLASS = PhiZDetector

    def parse(self, element):
        det1 = _DelimitedDetectorXMLHandler.parse(self, element)
        det2 = _ChannelsDetectorXMLHandler.parse(self, element)
        det3 = _TransitionsDetectorXMLHandler.parse(self, element)
        return PhiZDetector(det1.elevation_rad, det1.azimuth_rad,
                            det2.channels, det3.transitions)

    def convert(self, obj):
        element1 = _DelimitedDetectorXMLHandler.convert(self, obj)
        element2 = _ChannelsDetectorXMLHandler.convert(self, obj)
        element1.extend(element2)
        element3 = _TransitionsDetectorXMLHandler.convert(self, obj)
        element1.extend(element3)
        return element1

class PhotonRadialDetectorXMLHandler(_DelimitedDetectorXMLHandler,
                                     _ChannelsDetectorXMLHandler,
                                     _TransitionsDetectorXMLHandler):

    TAG = '{http://pymontecarlo.sf.net}photonRadialDetector'
    CLASS = PhotonRadialDetector

    def parse(self, element):
        det1 = _DelimitedDetectorXMLHandler.parse(self, element)
        det2 = _ChannelsDetectorXMLHandler.parse(self, element)
        det3 = _TransitionsDetectorXMLHandler.parse(self, element)
        return PhotonRadialDetector(det1.elevation_rad, det1.azimuth_rad,
                                    det2.channels, det3.transitions)

    def convert(self, obj):
        element1 = _DelimitedDetectorXMLHandler.convert(self, obj)
        element2 = _ChannelsDetectorXMLHandler.convert(self, obj)
        element1.extend(element2)
        element3 = _TransitionsDetectorXMLHandler.convert(self, obj)
        element1.extend(element3)
        return element1

class PhotonEmissionMapDetectorXMLHandler(_DelimitedDetectorXMLHandler):

    TAG = '{http://pymontecarlo.sf.net}photonEmissionMapDetector'
    CLASS = PhotonEmissionMapDetector

    def parse(self, element):
        det = _DelimitedDetectorXMLHandler.parse(self, element)

        subelement = element.find('xbins')
        if subelement is None:
            raise ValueError("Element 'xbins' not found")
        xbins = self._parse_numerical_parameter(subelement)

        subelement = element.find('ybins')
        if subelement is None:
            raise ValueError("Element 'ybins' not found")
        ybins = self._parse_numerical_parameter(subelement)

        subelement = element.find('zbins')
        if subelement is None:
            raise ValueError("Element 'zbins' not found")
        zbins = self._parse_numerical_parameter(subelement)

        return PhotonEmissionMapDetector(det.elevation_rad, det.azimuth_rad,
                                         xbins, ybins, zbins)

    def convert(self, obj):
        element = _DelimitedDetectorXMLHandler.convert(self, obj)

        subelement = etree.SubElement(element, 'xbins')
        self._convert_numerical_parameter(subelement, obj.xbins)

        subelement = etree.SubElement(element, 'ybins')
        self._convert_numerical_parameter(subelement, obj.ybins)

        subelement = etree.SubElement(element, 'zbins')
        self._convert_numerical_parameter(subelement, obj.zbins)

        return element

class PhotonIntensityDetectorXMLHandler(_DelimitedDetectorXMLHandler,
                                        _TransitionsDetectorXMLHandler):

    TAG = '{http://pymontecarlo.sf.net}photonIntensityDetector'
    CLASS = PhotonIntensityDetector

    def parse(self, element):
        det1 = _DelimitedDetectorXMLHandler.parse(self, element)
        det2 = _TransitionsDetectorXMLHandler.parse(self, element)
        return PhotonIntensityDetector(det1.elevation_rad, det1.azimuth_rad,
                                       det2.transitions)

    def convert(self, obj):
        element1 = _DelimitedDetectorXMLHandler.convert(self, obj)
        element2 = _TransitionsDetectorXMLHandler.convert(self, obj)
        element1.extend(element2)
        return element1

class TimeDetectorXMLHandler(_XMLHandler):

    TAG = '{http://pymontecarlo.sf.net}timeDetector'
    CLASS = TimeDetector

class ElectronFractionDetectorXMLHandler(_XMLHandler):

    TAG = '{http://pymontecarlo.sf.net}electronFractionDetector'
    CLASS = ElectronFractionDetector

class ShowersStatisticsDetectorXMLHandler(_XMLHandler):

    TAG = '{http://pymontecarlo.sf.net}showersStatisticsDetector'
    CLASS = ShowersStatisticsDetector

class TrajectoryDetectorXMLHandler(_XMLHandler):

    TAG = '{http://pymontecarlo.sf.net}trajectoryDetector'
    CLASS = TrajectoryDetector

    def parse(self, element):
        subelement = element.find('secondary')
        if subelement is None:
            raise ValueError("Element 'secondary' not found")
        secondary = self._parse_bool_parameter(subelement)

        return TrajectoryDetector(secondary)

    def convert(self, obj):
        element = _XMLHandler.convert(self, obj)

        subelement = etree.SubElement(element, 'secondary')
        self._convert_bool_parameter(subelement, obj.secondary)

        return element
