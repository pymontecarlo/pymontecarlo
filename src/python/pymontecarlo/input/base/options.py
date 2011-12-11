"""
================================================================================
:mod:`options` -- Main class containing all options of a simulation
================================================================================

.. module:: options
   :synopsis: Main class containing all options of a simulation

.. inheritance-diagram:: pymontecarlo.input.options

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from xml.etree.ElementTree import Element
from collections import MutableMapping, MutableSet

# Third party modules.

# Local modules.
from pymontecarlo.util.xmlutil import objectxml
from pymontecarlo.input.base.beam import GaussianBeam
from pymontecarlo.input.base.material import pure
from pymontecarlo.input.base.geometry import Substrate

# Globals and constants variables.

class _Detectors(MutableMapping):
    def __init__(self):
        self._data = {}

    def __len__(self):
        return self._data.__len__()

    def __getitem__(self, key):
        return self._data.__getitem__(key)

    def __delitem__(self, key):
        return self._data.__delitem__(key)

    def __setitem__(self, key, value):
        return self._data.__setitem__(key, value)

    def __iter__(self):
        return self._data.__iter__()

    def findall(self, clasz):
        return dict([(key, obj) for key, obj in self.iteritems() if isinstance(obj, clasz)])

class _Limits(MutableSet):
    def __init__(self):
        self._data = {}

    def __len__(self):
        return self._data.__len__()

    def __iter__(self):
        return self._data.values().__iter__()

    def __contains__(self, item):
        return item in self._data.values()

    def add(self, item):
        clasz = item.__class__
        self._data[hash(clasz)] = item

    def discard(self, item):
        self._data.pop(hash(item.__class__))

    def find(self, clasz, default=None):
        return self._data.get(hash(clasz), default)

class Options(objectxml):

    def __init__(self, name='Untitled'):
        """
        
        """
        self.name = name
        self.beam = GaussianBeam(1e3, 1e-8) # 1 keV, 10 nm
        self.geometry = Substrate(pure(79)) # Au substrate
        self._detectors = _Detectors()
        self._limits = _Limits()

    def __repr__(self):
        return '<%s(name=%s)>' % (self.__class__.__name__, self.name)

    def __str__(self):
        return self.name

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        options = cls(element.get('name'))

        child = list(element.find("beam"))[0]
        options.beam = objectxml.from_xml(child, *args, **kwargs)

        child = list(element.find("geometry"))[0]
        options.geometry = objectxml.from_xml(child, *args, **kwargs)

        children = list(element.find("detectors"))
        for child in children:
            key = child.get('_key')
            options.detectors[key] = objectxml.from_xml(child, *args, **kwargs)

        children = list(element.find("limits"))
        for child in children:
            options.limits.add(objectxml.from_xml(child, *args, **kwargs))

        return options

    def __savexml__(self, element, *args, **kwargs):
        element.set('name', self.name)

        child = Element('beam')
        child.append(self.beam.to_xml())
        element.append(child)

        child = Element('geometry')
        child.append(self.geometry.to_xml())
        element.append(child)

        child = Element('detectors')
        for key, detector in self.detectors.iteritems():
            grandchild = detector.to_xml()
            grandchild.set('_key', key)
            child.append(grandchild)
        element.append(child)

        child = Element('limits')
        for limit in self.limits:
            child.append(limit.to_xml())
        element.append(child)

    @property
    def beam(self):
        return self._beam

    @beam.setter
    def beam(self, beam):
        self._beam = beam

    @property
    def geometry(self):
        return self._geometry

    @geometry.setter
    def geometry(self, geometry):
        self._geometry = geometry

    @property
    def detectors(self):
        return self._detectors

    @property
    def limits(self):
        return self._limits

