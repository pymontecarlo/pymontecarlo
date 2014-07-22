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
from collections import MutableSet

# Third party modules.
import numpy as np

# Local modules.
from pymontecarlo.options.beam import _Beam, GaussianBeam
from pymontecarlo.options.material import VACUUM
from pymontecarlo.options.geometry import _Geometry, Substrate
from pymontecarlo.options.detector import _Detector
from pymontecarlo.options.limit import _Limit
from pymontecarlo.options.model import _Model

from pymontecarlo.program.config import Program

from pymontecarlo.settings import get_settings

from pymontecarlo.util.parameter import \
    (ParameterizedMetaclass, Parameter, ParameterizedMutableMapping,
     ParameterizedMutableSet)

# Globals and constants variables.

class _Programs(MutableSet):

    def __init__(self):
        self._programs = {}

    def __contains__(self, x):
        return x in self._programs.keys() or x in self._programs.values()

    def __iter__(self):
        for program in self._programs.values():
            if program is not None:
                yield program

    def __len__(self):
        return len(self._programs)

    def __repr__(self):
        return '<Programs(%s)>' % ','.join(map(str, self))

    def add(self, value):
        if isinstance(value, Program):
            alias = value.alias
            program = value
        else:
            alias = value
            try:
                program = get_settings().get_program(alias, validate=False)
            except ValueError:
                program = None
        self._programs[alias] = program

    def discard(self, value):
        if isinstance(value, Program):
            value = value.alias
        self._programs.pop(value)

    def update(self, values):
        for value in values:
            self.add(value)

    def aliases(self):
        return iter(self._programs.keys())

class _Detectors(ParameterizedMutableMapping):

    def iterclass(self, clasz):
        """
        Iterates over all detectors that are an instance of the specified class.
        Each iteration returns:

            * name/key of the detector
            * detector object
        """
        for key, parameter in self.__parameters__.items():
            detectors = parameter.__get__(self, simplify=False)
            for detector in detectors.flat:
                if isinstance(detector, clasz):
                    yield key, detector

class _Limits(ParameterizedMutableSet):

    def _get_key(self, item):
        return str(hash(item.__class__))

    def iterclass(self, clasz):
        """
        Iterates over all limits that are an instance of the specified class.
        Each iterations returns one limit object.
        """
        return (limit for limit in self if isinstance(limit, clasz))

class _Models(ParameterizedMutableSet):

    def __len__(self):
        length = 0
        for parameter in self.__parameters__.values():
            length += len(np.array(parameter.__get__(self), ndmin=1))
        return length

    def __iter__(self):
        for parameter in self.__parameters__.values():
            yield from np.array(parameter.__get__(self), ndmin=1)

    def __contains__(self, item):
        key = self._get_key(item)
        if key not in self.__parameters__:
            return False

        parameter = self.__parameters__[key]
        return item in parameter.__get__(self)

    def _get_key(self, item):
        return item.type.name

    def add(self, item):
        key = self._get_key(item)

        try:
            parameter = self.__parameters__[key]
        except KeyError:
            parameter = Parameter(*self._parameter_args, **self._parameter_kwargs)
            parameter._name = key
            self.__parameters__[key] = parameter
            parameter.__set__(self, item)
        else:
            items = set(np.array(parameter.__get__(self), ndmin=1))
            items.add(item)
            parameter.__set__(self, list(items))

    def discard(self, item):
        key = self._get_key(item)
        if key not in self.__parameters__:
            raise KeyError(key)

        parameter = self.__parameters__[key]
        items = set(np.array(parameter.__get__(self), ndmin=1))
        items.discard(item)

        if not items:
            del self.__parameters__[key]
            del self.__dict__[key]
        else:
            parameter.__set__(self, list(items))

    def iterclass(self, type_):
        """
        Iterates over all models that are of the specified type.
        Each iteration returns one model.
        """
        return (model for model in self if model.type == type_)

class Options(object, metaclass=ParameterizedMetaclass):

    beam = Parameter(_Beam, doc="Beam")
    geometry = Parameter(_Geometry, doc="Geometry")
    detectors = Parameter(doc="Detector(s)")
    limits = Parameter(_Limits, required=False, doc="Limit(s)")
    models = Parameter(_Models, required=False, doc="Model(s)")

    @classmethod
    def read(cls, source):
        from pymontecarlo.fileformat.options.options import OptionsReader
        reader = OptionsReader()
        reader.read(source)
        return reader.get()

    @classmethod
    def fromelement(cls, element):
        from pymontecarlo.fileformat.options.options import OptionsReader
        reader = OptionsReader()
        reader.parse(element)
        return reader.get()

    def __init__(self, name='Untitled'):
        """
        Options for a simulation.

        The options of a simulation are grouped in 5 sub-properties:

          * :attr:`beam`: beam related options
          * :attr:`geometry`: geometry related options
          * :attr:`detectors`: detector(s) about what should be measured
          * :attr:`limits`: limit(s) when to stop the simulation
          * :attr:`models`: simulation models/algorithms

        :arg name: name of the simulation

        By default, the beam is set to a Gaussian beam of 10 nm with an incident
        energy of 1 keV.
        The geometry is a Au substrate.
        No detectors, limits or models are defined.
        """
        self._name = name
        self._uuid = uuid.uuid4().hex

        self._programs = _Programs()

        self.beam = GaussianBeam(1e3, 1e-8, origin_m=(0.0, 0.0, 0.01)) # 1 keV, 10 nm
        self.geometry = Substrate(VACUUM) # Au substrate

        # Hack because numpy converts MutableMapping to empty array
        detectors = np.ndarray((1,), np.dtype(_Detectors))
        detectors[0] = _Detectors(_Detector)
        self.__dict__['detectors'] = detectors

        self.limits = _Limits(_Limit)
        self.models = _Models(_Model)

    def __repr__(self):
        return '<%s(name=%s)>' % (self.__class__.__name__, str(self.name))

    def __str__(self):
        return self.name

    def __copy__(self):
        # From http://stackoverflow.com/questions/1500718/what-is-the-right-way-to-override-the-copy-deepcopy-operations-on-an-object-in-p
        cls = self.__class__
        result = cls.__new__(cls)

        result.__dict__.update(self.__dict__)
        result.__dict__['_uuid'] = uuid.uuid4().hex # Reset

        return result

    def __deepcopy__(self, memo):
        # http://stackoverflow.com/questions/1500718/what-is-the-right-way-to-override-the-copy-deepcopy-operations-on-an-object-in-p
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result

        for k, v in self.__dict__.items():
            result.__dict__[k] = deepcopy(v, memo)
        result.__dict__['_uuid'] = uuid.uuid4().hex # Reset

        return result

    def write(self, source):
        from pymontecarlo.fileformat.options.options import OptionsWriter
        writer = OptionsWriter()
        writer.write(self, source)
        writer.join()

    def toelement(self):
        from pymontecarlo.fileformat.options.options import OptionsWriter
        writer = OptionsWriter()
        writer.convert(self)
        return writer.get()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def uuid(self):
        return self._uuid

    @property
    def programs(self):
        return self._programs

