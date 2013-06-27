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

# Third party modules.

# Local modules.
from pymontecarlo.input.parameter import \
    (ParameterizedMetaClass, Parameter, SimpleValidator, CastValidator,
     ParameterizedMutableMapping, ParameterizedMutableSet)
from pymontecarlo.input.beam import PencilBeam, GaussianBeam
from pymontecarlo.input.material import pure
from pymontecarlo.input.geometry import Substrate
from pymontecarlo.input.model import Model

from pymontecarlo.input import mapper
from pymontecarlo.util.xmlmapper import Attribute, Element, PythonType, UserType

# Globals and constants variables.

FORBIDDEN_DETECTOR_KEYS = ['options', 'keys']

class _Detectors(ParameterizedMutableMapping):

    def __setitem__(self, key, value):
        if key in FORBIDDEN_DETECTOR_KEYS:
            raise KeyError, 'Detector cannot have the following keys: %s' % \
                        ', '.join(FORBIDDEN_DETECTOR_KEYS)
        return ParameterizedMutableMapping.__setitem__(self, key, value)

    def iterclass(self, clasz):
        for key, parameter in self.__parameters__.iteritems():
            wrapper = parameter._get_wrapper(self)
            for detector in wrapper:
                if isinstance(detector, clasz):
                    yield key, detector

class _Limits(ParameterizedMutableSet):

    def _get_key(self, item):
        return hash(item.__class__)

    def iterclass(self, clasz):
        parameter = self.__parameters__[hash(clasz)]
        wrapper = parameter._get_wrapper(self)
        return iter(wrapper)

class _Models(ParameterizedMutableSet):
    
    def _get_key(self, item):
        return item.type

    def find(self, type, default=None):
        return self.__parameters__.get(type, default).__get__(self)

    def iteritems(self):
        for type, parameter in self.__parameters__.iteritems():
            yield type, parameter.__get__(self)

_name_validator = SimpleValidator(lambda n: bool(n), "Name cannot be empty")

class Options(object):
    
    __metaclass__ = ParameterizedMetaClass
    
    VERSION = '5'

    name = Parameter(_name_validator, "Name")
    beam = Parameter(doc="Beam")
    geometry = Parameter(doc="Geometry")
    detectors = Parameter(doc="Detector(s)")
    limits = Parameter(doc="Limit(s)")
    models = Parameter([CastValidator(_Models)], "Model(s)")

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
        self.name = name
        self._uuid = None

        self.beam = GaussianBeam(1e3, 1e-8) # 1 keV, 10 nm

        self.geometry = Substrate(pure(79)) # Au substrate

        self.detectors = _Detectors()
        self.__parameters__['detectors'].freeze(self)

        self.limits = _Limits()
        self.__parameters__['limits'].freeze(self)

        self.models = _Models()

    def __repr__(self):
        return '<%s(name=%s)>' % (self.__class__.__name__, str(self.name))

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return unicode(self.name)
    
    def __getstate__(self):
        state = self.__dict__.copy()
        state['_uuid'] = None
        return state

#    @classmethod
#    def __loadxml__(cls, element, *args, **kwargs):
#        # Check version
#        version = element.get('version')
#        if version != cls.VERSION:
#            raise IOError, "Incorrect version of options %s. Only version %s is accepted" % \
#                    (version, cls.VERSION)
#
#        options = cls(element.get('name'))
#
#        # UUID
#        options._uuid = element.get('uuid')
#
#        # Beam
#        parent = element.find("beam")
#        if parent is None:
#            raise IOError, 'No beam defined.'
#        child = list(parent)[0]
#        options.beam = XMLIO.from_xml(child, *args, **kwargs)
#
#        # Geometry
#        parent = element.find("geometry")
#        if parent is None:
#            raise IOError, 'No geometry defined.'
#        child = list(parent)[0]
#        options.geometry = XMLIO.from_xml(child, *args, **kwargs)
#
#        parent = element.find('detectors')
#        if parent is not None:
#            for child in list(parent):
#                key = child.get('_key')
#                options.detectors[key] = XMLIO.from_xml(child, *args, **kwargs)
#
#        parent = element.find('limits')
#        if parent is not None:
#            for child in list(parent):
#                options.limits.add(XMLIO.from_xml(child, *args, **kwargs))
#
#        parent = element.find('models')
#        if parent is not None:
#            for child in list(parent):
#                options.models.add(XMLIO.from_xml(child, *args, **kwargs))
#
#        return options
#
#    def __savexml__(self, element, *args, **kwargs):
#        element.set('name', self.name)
#        if self._uuid: element.set('uuid', self.uuid)
#        element.set('version', self.VERSION)
#
#        child = Element('beam')
#        child.append(self.beam.to_xml())
#        element.append(child)
#
#        child = Element('geometry')
#        child.append(self.geometry.to_xml())
#        element.append(child)
#
#        child = Element('detectors')
#        for key in sorted(self.detectors.keys()):
#            detector = self.detectors[key]
#            grandchild = detector.to_xml()
#            grandchild.set('_key', key)
#            child.append(grandchild)
#        element.append(child)
#
#        child = Element('limits')
#        for limit in self.limits:
#            child.append(limit.to_xml())
#        element.append(child)
#
#        child = Element('models')
#        for model in self.models:
#            child.append(model.to_xml())
#        element.append(child)

    @property
    def uuid(self):
        """
        Unique identifier for this object.
        """
        if self._uuid is None:
            self._uuid = uuid.uuid4().hex
        return self._uuid

mapper.register(Options, '{http://pymontecarlo.sf.net}options',
                Attribute('VERSION', PythonType(str), 'version'),
                Attribute('name', PythonType(str)),
                Element('beam', UserType(PencilBeam), iterable=True),
                Element('models', UserType(Model), iterable=True),
                )

#XMLIO.register('{http://pymontecarlo.sf.net}options', Options)
#
#class _OptionsSequenceParameters(Sequence):
#
#    def __init__(self):
#        self._list_params = []
#
#    def __len__(self):
#        return len(self._list_params)
#
#    def __getitem__(self, index):
#        return self._list_params[index]
#
#class OptionsSequence(Sequence, objectxml):
#    """
#    :class:`.OptionsSequence` is a container of several :class:`.Options`.
#    It preserves the order of the options.
#    If a :class:`SequenceRunner` is used to simulate the options sequence, this
#    order will also be preserved in the resultant :class:`.ResultsSequence`.
#
#    The class works like any other :class:`list` object, except that an options
#    cannot be replaced by another options on the fly (:meth:`__setitem__`).
#    To replace an options, the user should remove the old options and insert
#    a new one.
#
#    The class also allows some parameter values to be associated with each
#    options.
#    Keyword arguments can be passed to the :meth:`append` and :meth:`insert`
#    methods::
#
#        >>> ops_seq.append(ops1, param1=1.0, param2=3.0)
#
#    The parameters are saved in a dictionary for each options.
#    Note that options can have different parameters.
#    Parameters can be retrieved and modified using the property
#    :attr:`parameters`::
#
#        >>> ops_seq.parameters[0]['param1'] = 2.0
#        >>> ops_seq.parameters[0]['param1']
#        >>> 2.0
#
#    """
#    VERSION = "1"
#
#    def __init__(self):
#        self._list_options = []
#        self._params = _OptionsSequenceParameters()
#
#    @classmethod
#    def __loadxml__(cls, element, *args, **kwargs):
#        # Check version
#        version = element.get('version')
#        if version != cls.VERSION:
#            raise IOError, "Incorrect version of options sequence %s. Only version %s is accepted" % \
#                    (version, cls.VERSION)
#
#        # Identifiers
#        identifiers = element.get('identifiers').split(',')
#
#        # Read options
#        list_options = {}
#        list_params = {}
#
#        for child in element.iter('{http://pymontecarlo.sf.net}options'):
#            options = Options.from_xml(child)
#
#            identifier = options.uuid
#            list_options[identifier] = options
#
#            params = {}
#            for grandchild in child.iter('param'):
#                key = grandchild.get('key')
#                value = grandchild.get('value')
#                try:
#                    value = ast.literal_eval(value) # Parse to Python object
#                except ValueError:
#                    pass
#                params[key] = value
#
#            list_params[identifier] = params
#
#        # Build sequence
#        options_seq = cls()
#
#        if len(identifiers) != len(list_options):
#            raise IOError, 'Number of identifiers do not match number of options'
#
#        for identifier in identifiers:
#            options_seq.append(list_options[identifier], **list_params[identifier])
#
#        return options_seq
#
#    def __savexml__(self, element, *args, **kwargs):
#        element.set('version', self.VERSION)
#
#        identifiers = []
#        for options, params in zip(self, self._params):
#            identifiers.append(options.uuid)
#
#            child = options.to_xml()
#
#            for key, value in params.iteritems():
#                grandchild = Element('param')
#                grandchild.set('key', str(key))
#                grandchild.set('value', str(value))
#                child.append(grandchild)
#
#            element.append(child)
#
#        element.set('identifiers', ','.join(identifiers))
#
#    def __repr__(self):
#        return '<%s(%i options)>' % (self.__class__.__name__, len(self))
#
#    def __len__(self):
#        return len(self._list_options)
#
#    def __getitem__(self, index):
#        return self._list_options[index]
#
#    def __delitem__(self, index):
#        del self._list_options[index]
#        del self._params._list_params[index]
#
#    def append(self, options, **params):
#        self.insert(len(self), options, **params)
#
#    def insert(self, index, options, **params):
#        if options in self:
#            raise ValueError, "Options already added"
#        self._list_options.insert(index, options)
#        self._params._list_params.insert(index, params.copy())
#
#    def remove(self, options):
#        del self[self.index(options)]
#
#    def pop(self, index= -1):
#        v = self[index]
#        del self[index]
#        return v
#
#    @property
#    def parameters(self):
#        return self._params
#
#    params = parameters
#
##XMLIO.register('{http://pymontecarlo.sf.net}optionsSequence', OptionsSequence)
