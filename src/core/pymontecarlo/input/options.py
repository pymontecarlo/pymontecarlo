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
from copy import deepcopy

# Third party modules.

# Local modules.
from pymontecarlo.input.parameter import \
    (ParameterizedMetaClass, Parameter, FrozenParameter, SimpleValidator,
     ParameterizedMutableMapping, ParameterizedMutableSet)
from pymontecarlo.input.beam import _Beam, GaussianBeam
from pymontecarlo.input.material import pure
from pymontecarlo.input.geometry import _Geometry, Substrate
from pymontecarlo.input.detector import _Detector
from pymontecarlo.input.limit import _Limit
from pymontecarlo.input.model import Model
from pymontecarlo.input.xmlmapper import \
    (mapper, Attribute, ParameterizedElement, ParameterizedElementSet,
     ParameterizedElementDict, PythonType, UserType)

# Globals and constants variables.

class _Detectors(ParameterizedMutableMapping):

    def iterclass(self, clasz):
        for key, parameter in self.__parameters__.iteritems():
            wrapper = parameter._get_wrapper(self)
            for detector in wrapper:
                if isinstance(detector, clasz):
                    yield key, detector

class _Limits(ParameterizedMutableSet):

    def iterclass(self, clasz):
        return (limit for limit in self if isinstance(limit, clasz))

class _Models(ParameterizedMutableSet):
    
    def iterclass(self, type_):
        return (model for model in self if model.type == type_)

_name_validator = SimpleValidator(lambda n: bool(n), "Name cannot be empty")

class Options(object):
    
    __metaclass__ = ParameterizedMetaClass
    
    VERSION = '6'

    name = Parameter(_name_validator, "Name")
    beam = Parameter(doc="Beam")
    geometry = Parameter(doc="Geometry")
    detectors = FrozenParameter(_Detectors, "Detector(s)")
    limits = FrozenParameter(_Limits, "Limit(s)")
    models = FrozenParameter(_Models, "Model(s)")

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

    def __repr__(self):
        return '<%s(name=%s)>' % (self.__class__.__name__, str(self.name))

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return unicode(self.name)
    
    def __copy__(self):
        # From http://stackoverflow.com/questions/1500718/what-is-the-right-way-to-override-the-copy-deepcopy-operations-on-an-object-in-p
        cls = self.__class__
        result = cls.__new__(cls)

        result.__dict__.update(self.__dict__)
        result.__dict__['_uuid'] = None

        return result

    def __deepcopy__(self, memo):
        # http://stackoverflow.com/questions/1500718/what-is-the-right-way-to-override-the-copy-deepcopy-operations-on-an-object-in-p
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result

        for k, v in self.__dict__.items():
            result.__dict__[k] = deepcopy(v, memo)
        result.__dict__['_uuid'] = None

        return result

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
                Attribute('_uuid', PythonType(str), 'uuid'),
                ParameterizedElement('beam', UserType(_Beam)),
                ParameterizedElement('geometry', UserType(_Geometry)),
                ParameterizedElementDict('detectors', PythonType(str), UserType(_Detector)),
                ParameterizedElementSet('limits', UserType(_Limit)),
                ParameterizedElementSet('models', UserType(Model)),
                )

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
