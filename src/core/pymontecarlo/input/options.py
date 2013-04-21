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

__all__ = ['Options']

# Standard library modules.
import uuid
from collections import MutableMapping, MutableSet, Sequence

# Third party modules.

# Local modules.
from pymontecarlo.util.xmlutil import XMLIO, Element, objectxml
from pymontecarlo.input.option import Option
from pymontecarlo.input.beam import GaussianBeam
from pymontecarlo.input.material import pure
from pymontecarlo.input.geometry import Substrate

# Globals and constants variables.

# Load submodules to register XML loader and saver
import pymontecarlo.input.beam #@UnusedImport
import pymontecarlo.input.geometry #@UnusedImport
import pymontecarlo.input.detector #@UnusedImport
import pymontecarlo.input.limit #@UnusedImport
import pymontecarlo.input.model #@UnusedImport

FORBIDDEN_DETECTOR_KEYS = ['options', 'keys']

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
        if key in FORBIDDEN_DETECTOR_KEYS:
            raise KeyError, 'Detector cannot have the following keys: %s' % \
                        ', '.join(FORBIDDEN_DETECTOR_KEYS)
        return self._data.__setitem__(key, value)

    def __iter__(self):
        return self._data.__iter__()

    def findall(self, clasz):
        return dict([(key, obj) for key, obj in self.iteritems() if isinstance(obj, clasz)])

    def find(self, detector):
        for key, val in self.iteritems():
            if detector is val:
                return key

        raise ValueError, 'Detector not found: %s' % detector

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
        key = hash(item.__class__)
        self._data[key] = item

    def discard(self, item):
        self._data.pop(hash(item.__class__))

    def find(self, clasz, default=None):
        return self._data.get(hash(clasz), default)

class _Models(MutableSet):
    def __init__(self):
        self._data = {}

    def __len__(self):
        return self._data.__len__()

    def __iter__(self):
        return self._data.values().__iter__()

    def __contains__(self, item):
        return item in self._data.values()

    def add(self, item):
        key = item.type
        self._data[key] = item

    def discard(self, item):
        self._data.pop(item.type)

    def find(self, type, default=None):
        return self._data.get(type, default)

    def items(self):
        return self._data.items()

class Options(Option):
    VERSION = '5'

    def __init__(self, name='Untitled'):
        """
        Options for a simulation.
        
        The options of a simulation are grouped in 5 sub-properties:
        
          * :attr:`beam`: beam related options
          * :attr:`geometry`: geometry related options
          * :attr:`detectors`: detector(s) about what should be measured
          * :attr:`limits`: limit(s) when to stop the simulation
          * :attr:`models`: simulation models/algorithms
        
        :arg name: name of the simulation (unicode accepted)
        
        By default, the beam is set to a Gaussian beam of 10 nm with an incident
        energy of 1 keV.
        The geometry is a Au substrate.
        No detectors, limits or models are defined.
        """
        Option.__init__(self)

        self.name = name
        self.beam = GaussianBeam(1e3, 1e-8) # 1 keV, 10 nm
        self.geometry = Substrate(pure(79)) # Au substrate
        self._props['detectors'] = _Detectors()
        self._props['limits'] = _Limits()
        self._props['models'] = _Models()

    def __repr__(self):
        return '<%s(name=%s)>' % (self.__class__.__name__, str(self.name))

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return unicode(self.name)

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        # Check version
        version = element.get('version')
        if version != cls.VERSION:
            raise IOError, "Incorrect version of options %s. Only version %s is accepted" % \
                    (version, cls.VERSION)

        options = cls(element.get('name'))

        # Beam
        parent = element.find("beam")
        if parent is None:
            raise IOError, 'No beam defined.'
        child = list(parent)[0]
        options.beam = XMLIO.from_xml(child, *args, **kwargs)

        # Geometry
        parent = element.find("geometry")
        if parent is None:
            raise IOError, 'No geometry defined.'
        child = list(parent)[0]
        options.geometry = XMLIO.from_xml(child, *args, **kwargs)

        parent = element.find('detectors')
        if parent is not None:
            for child in list(parent):
                key = child.get('_key')
                options.detectors[key] = XMLIO.from_xml(child, *args, **kwargs)

        parent = element.find('limits')
        if parent is not None:
            for child in list(parent):
                options.limits.add(XMLIO.from_xml(child, *args, **kwargs))

        parent = element.find('models')
        if parent is not None:
            for child in list(parent):
                options.models.add(XMLIO.from_xml(child, *args, **kwargs))

        return options

    def __savexml__(self, element, *args, **kwargs):
        element.set('name', self.name)
        element.set('version', self.VERSION)

        child = Element('beam')
        child.append(self.beam.to_xml())
        element.append(child)

        child = Element('geometry')
        child.append(self.geometry.to_xml())
        element.append(child)

        child = Element('detectors')
        for key in sorted(self.detectors.keys()):
            detector = self.detectors[key]
            grandchild = detector.to_xml()
            grandchild.set('_key', key)
            child.append(grandchild)
        element.append(child)

        child = Element('limits')
        for limit in self.limits:
            child.append(limit.to_xml())
        element.append(child)

        child = Element('models')
        for model in self.models:
            child.append(model.to_xml())
        element.append(child)

    @property
    def name(self):
        """
        Name of these simulation options.
        """
        return self._props['name']

    @name.setter
    def name(self, name):
        if not name:
            raise ValueError, 'Name cannot be empty'
        self._props['name'] = unicode(name)

    @property
    def beam(self):
        """
        Options about the beam.
        """
        return self._props['beam']

    @beam.setter
    def beam(self, beam):
        self._props['beam'] = beam

    @property
    def geometry(self):
        """
        Options about the geometry.
        
        .. warning:: 
        
           Some geometries may not be available for all simulation programs.
           The converter of a program will raise an exception about 
           incompatible geometries.
           
        """
        return self._props['geometry']

    @geometry.setter
    def geometry(self, geometry):
        self._props['geometry'] = geometry

    @property
    def detectors(self):
        """
        Options about the detectors.
        Detectors define what should be measured during the simulation.
        
        This is a read-only property.
        This property is a :class:`dict` where the keys are the name of 
        detectors and the values are the detector object. 
        
        .. warning:: 
        
           Some detectors may not be available for all simulation programs.
           The converter of a program will warn you and remove incompatible 
           detectors.
        
        """
        return self._props['detectors']

    @property
    def limits(self):
        """
        Options about the limits.
        Limits define when a simulation should halt.
        
        This is a read-only property.
        This property is a :class:`set` to prevent multiple limits of the 
        same type.
        A limit can be added using the method :meth:`add`.
        
        .. note::
        
           It is advisable to have at least one limit. 
           If not, the simulation may never end depending on the simulation
           program.
        
        .. warning:: 
        
           Some limits may not be available for all simulation programs.
           The converter of a program will warn you and remove incompatible 
           limits.
        """
        return self._props['limits']

    @property
    def models(self):
        """
        Options about simulation models/algorithms.
        
        This is a read-only property.
        This property is a class:`set` to prevent multiple models of the 
        same type.
        A model can be added using the method :meth:`add`.
        
        .. warning:: 
        
           Some models may not be available for all simulation programs.
           The converter of a program will warn you and remove incompatible 
           models.
           The converter will also add missing default models for the simulation 
           program.
        """
        return self._props['models']

XMLIO.register('{http://pymontecarlo.sf.net}options', Options)

class _OptionsSequenceParameters(Sequence):

    def __init__(self):
        self._list_params = []

    def __repr__(self):
        return '<%s(%i options)>' % (self.__class__.__name__, len(self))

    def __len__(self):
        return len(self._list_params)

    def __getitem__(self, index):
        return self._list_params[index]

class OptionsSequence(Sequence, objectxml):
    VERSION = "1"

    def __init__(self):
        self._list_options = []
        self._params = _OptionsSequenceParameters()

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        # Check version
        version = element.get('version')
        if version != cls.VERSION:
            raise IOError, "Incorrect version of options sequence %s. Only version %s is accepted" % \
                    (version, cls.VERSION)

        # Identifiers
        identifiers = element.get('identifiers').split(',')

        # Read options
        list_options = {}
        list_params = {}

        for child in element.iter('{http://pymontecarlo.sf.net}options'):
            identifier = child.get('uuid')

            options = Options.from_xml(child)
            list_options[identifier] = options
            
            params = {}
            for grandchild in child.iter('param'):
                key = grandchild.get('key')
                value = float(grandchild.get('value'))
                params[key] = value

            list_params[identifier] = params

        # Build sequence
        options_seq = cls()

        if len(identifiers) != len(list_options):
            raise IOError, 'Number of identifiers do not match number of options'

        for identifier in identifiers:
            options_seq.append(list_options[identifier], **list_params[identifier])

        return options_seq

    def __savexml__(self, element, *args, **kwargs):
        element.set('version', self.VERSION)

        identifiers = []
        for options, params in zip(self, self._params):
            identifier = uuid.uuid4().hex
            identifiers.append(identifier)

            child = options.to_xml()
            child.set('uuid', identifier)

            for key, value in params.iteritems():
                grandchild = Element('param')
                grandchild.set('key', str(key))
                grandchild.set('value', str(value))
                child.append(grandchild)

            element.append(child)

        element.set('identifiers', ','.join(identifiers))

    def __repr__(self):
        return '<%s(%i options)>' % (self.__class__.__name__, len(self))

    def __len__(self):
        return len(self._list_options)

    def __getitem__(self, index):
        return self._list_options[index]

    def __delitem__(self, index):
        del self._list_options[index]
        del self._params._list_params[index]

    def append(self, options, **params):
        self.insert(len(self), options, **params)

    def insert(self, index, options, **params):
        self._list_options.insert(index, options)
        self._params._list_params.insert(index, params.copy())

    def remove(self, options):
        del self[self.index(options)]

    def pop(self, index= -1):
        v = self[index]
        del self[index]
        return v

    @property
    def parameters(self):
        return self._params

    params = parameters

XMLIO.register('{http://pymontecarlo.sf.net}optionsSequence', OptionsSequence)
