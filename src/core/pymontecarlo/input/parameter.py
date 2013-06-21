#!/usr/bin/env python
"""
================================================================================
:mod:`parameter` -- Base classes for parameters
================================================================================

.. module:: parameter
   :synopsis: Base classes for parameters

.. inheritance-diagram:: pymontecarlo.input.parameter

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import math
from abc import ABCMeta, abstractmethod
from collections import MutableSet, MutableMapping, Mapping, Iterable
import copy
from operator import itemgetter

# Third party modules.

# Local modules.
from pymontecarlo.util.multipleloop import combine

# Globals and constants variables.

class ParameterizedMetaClass(type):

    def __new__(cls, clsname, bases, methods):
        parameters = {}

        # Parameters from parents
        parents = [b for b in bases if isinstance(b, ParameterizedMetaClass)]
        for base in parents:
            parameters.update(base.__parameters__)

        # Attach attribute names to parameters
        for key, value in methods.items():
            if isinstance(value, Parameter):
                value._new(cls, clsname, bases, methods, key)
                parameters[value.name] = value

        # Add __parameters__ attribute
        methods['__parameters__'] = parameters

        return type.__new__(cls, clsname, bases, methods)

class _ParameterValuesWrapper(object):

    def __init__(self, values):
        self._values = tuple(values)
        self._frozen = False

    def __repr__(self):
        format = '<%s(%s, frozen)>' if self.is_frozen() else '<%s(%s)>'
        return format % (self.__class__.__name__, str(self._values))

    def __iter__(self):
        return iter(self._values)

    def __len__(self):
        return len(self._values)

    def __add__(self, other):
        if self.is_frozen():
            raise ValueError, "Frozen parameter"
        return self.__class__([v + other if v is not None else None \
                               for v in self._values])

    def __sub__(self, other):
        if self.is_frozen():
            raise ValueError, "Frozen parameter"
        return self.__class__([v - other if v is not None else None \
                               for v in self._values])

    def __mul__(self, other):
        if self.is_frozen():
            raise ValueError, "Frozen parameter"
        return self.__class__([v * other if v is not None else None \
                               for v in self._values])

    def __div__(self, other):
        if self.is_frozen():
            raise ValueError, "Frozen parameter"
        return self.__class__([v / other if v is not None else None \
                               for v in self._values])

    def __eq__(self, other):
        return all([v == other for v in self._values])

    def __ne__(self, other):
        return all([v != other for v in self._values])

    def __lt__(self, other):
        return all([v < other for v in self._values])

    def __le__(self, other):
        return all([v <= other for v in self._values])

    def __gt__(self, other):
        return all([v > other for v in self._values])

    def __ge__(self, other):
        return all([v >= other for v in self._values])

    def __contains__(self, item):
        return all([item in v for v in self._values])

    def get(self):
        if len(self._values) == 1:
            return self._values[0]
        else:
            return list(self._values)

    def freeze(self):
        self._frozen = True

    def is_frozen(self):
        return self._frozen

_PASS_WRAPPER = _ParameterValuesWrapper(())

class Parameter(object):

    def __init__(self, validators=None, doc=None):
        self._name = None
        self.__doc__ = doc

        if validators is None:
            validators = [PassValidator()]
        if not hasattr(validators, '__iter__'):
            validators = [validators]
        self._validators = validators

    def __repr__(self):
        return '<%s(%s)>' % (self.__class__.__name__, self.name)

    def __get__(self, obj, objtype=None):
        return self._get_wrapper(obj, objtype).get()
    
    def _get_wrapper(self, obj, objtype=None):
        if not obj.__dict__.has_key(self.name):
            raise AttributeError, "No value"
        return obj.__dict__[self.name]

    def __set__(self, obj, values):
        obj.__dict__[self.name] = self._create_wrapper(obj, values)
    
    def _create_wrapper(self, obj, values):
        if obj.__dict__.get(self.name, _PASS_WRAPPER).is_frozen():
            raise AttributeError, "Frozen parameter"

        if not isinstance(values, list):
            values = (values,)

        valid_values = []
        for value in values:
            valid_value = value
            for validator in self._validators:
                valid_value = validator.validate(valid_value)
            valid_values.append(valid_value)

        return _ParameterValuesWrapper(valid_values)

    def _new(self, cls, clsname, bases, methods, name):
        self._name = name

    def freeze(self, obj):
        obj.__dict__[self.name].freeze()

    @property
    def name(self):
        return self._name

class ParameterAlias(object):

    def __init__(self, alias, doc=None):
        self.__doc__ = doc
        self._alias = alias

    def __repr__(self):
        return '<%s(%s)>' % (self.__class__.__name__, self._alias.name)

    def __get__(self, obj, objtype=None):
        return self._get_wrapper(obj, objtype).get()

    def _get_wrapper(self, obj, objtype=None):
        return self._alias._get_wrapper(obj, objtype)

    def __set__(self, obj, values):
        obj.__dict__[self._alias.name] = self._create_wrapper(obj, values)

    def _create_wrapper(self, obj, values):
        return self._alias._create_wrapper(obj, values)

class ParameterizedMutableSet(MutableSet):

    def __init__(self, validators=None):
        self._validators = validators
        self.__parameters__ = {}

    def __repr__(self):
        valstr = ', '.join(map(str, self))
        return '<%s(%s)>' % (self.__class__.__name__, valstr)

    def __len__(self):
        return len(self.__parameters__)

    def __iter__(self):
        for parameter in self.__parameters__.itervalues():
            yield parameter.__get__(self)

    def __contains__(self, item):
        return self._get_key(item) in self.__parameters__

    def _get_key(self, item):
        return hash(item)

    def add(self, item):
        key = self._get_key(item)

        try:
            parameter = self.__parameters__[key]
        except KeyError:
            parameter = Parameter(self._validators)
            parameter._name = key
            self.__parameters__[key] = parameter

        parameter.__set__(self, item)

    def discard(self, item):
        key = self._get_key(item)
        if key not in self.__parameters__:
            raise KeyError
        return self.__parameters__[key].__get__(self)

class ParameterizedMutableMapping(MutableMapping):

    def __init__(self, validators=None):
        self._validators = validators
        self.__parameters__ = {}

    def __repr__(self):
        valstr = ', '.join(['%s: %s' % item for item in self.items()])
        return '<%s(%s)>' % (self.__class__.__name__, valstr)

    def __len__(self):
        return len(self.__parameters__)

    def __getitem__(self, key):
        if key not in self.__parameters__:
            raise KeyError
        return self.__parameters__[key].__get__(self)

    def __delitem__(self, key):
        if key not in self.__parameters__:
            raise KeyError
        return self.__parameters__.pop(key)

    def __setitem__(self, key, value):
        try:
            parameter = self.__parameters__[key]
        except KeyError:
            parameter = Parameter(self._validators)
            parameter._name = key
            self.__parameters__[key] = parameter

        parameter.__set__(self, value)

    def __iter__(self):
        return iter(self.__parameters__)

class FactorParameterAlias(ParameterAlias):
    """
    Multiplies the set value(s) by the specified factor before passing them 
    to the alias parameter and divides the returned value(s) from the
    alias parameter by the specified factor.
    """

    def __init__(self, alias, factor):
            ParameterAlias.__init__(self, alias)
            self._factor = factor

    def _get_wrapper(self, obj, objtype=None):
        return ParameterAlias._get_wrapper(self, obj, objtype) / self._factor

    def _create_wrapper(self, obj, values):
        return ParameterAlias._create_wrapper(self, obj, values) * self._factor

class AngleParameter(Parameter):
    
    def _new(self, cls, clsname, bases, methods, name):
        parameter = methods.pop(name)
        methods[name + '_rad'] = parameter
        methods[name + '_deg'] = FactorParameterAlias(parameter, math.pi / 180.0)
        Parameter._new(self, cls, clsname, bases, methods, name + '_rad')

class UnitParameter(Parameter):
    
    _prefix = {'y': 1e-24, # yocto
               'z': 1e-21, # zepto
               'a': 1e-18, # atto
               'f': 1e-15, # femto
               'p': 1e-12, # pico
               'n': 1e-9, # nano
               'u': 1e-6, # micro
               'm': 1e-3, # mili
               'c': 1e-2, # centi
               'd': 1e-1, # deci
               'k': 1e3, # kilo
               'M': 1e6, # mega
               'G': 1e9, # giga
               'T': 1e12, # tera
               'P': 1e15, # peta
               'E': 1e18, # exa
               'Z': 1e21, # zetta
               'Y': 1e24} # yotta
    
    def __init__(self, unit, validators=None, doc=None):
        Parameter.__init__(self, validators, doc)
        self._unit = unit

    def _new(self, cls, clsname, bases, methods, name):
        parameter = methods.pop(name)
        methods[name + '_' + self._unit] = parameter
        
        for prefix, factor in self._prefix.iteritems():
            methods['%s_%s%s' % (name, prefix, self._unit)] = \
                FactorParameterAlias(parameter, factor)

        Parameter._new(self, cls, clsname, bases, methods, name + "_" + self._unit)

class TimeParameter(Parameter):

    _factors = {'year': 31536000.0,
                'month': 2628000.0,
                'day': 86400.0,
                'hr': 3600.0,
                'min': 60.0,
                's': 1.0}

    def _new(self, cls, clsname, bases, methods, name):
        parameter = methods.pop(name)

        for unit, factor in self._factors.iteritems():
            methods['%s_%s' % (name, unit)] = \
                FactorParameterAlias(parameter, factor)

        Parameter._new(self, cls, clsname, bases, methods, name + '_s')

class _Validator(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def validate(self, value):
        raise NotImplementedError

class PassValidator(_Validator):

    def validate(self, value):
        return value

class SimpleValidator(_Validator):

    def __init__(self, func, message=None):
        if not callable(func):
            raise ValueError, "Validation function must be callable"
        self._func = func
        self._message = message

    def validate(self, value):
        if not self._func(value):
            raise ValueError, self._message or "Invalid value(s)"
        return value

class EnumValidator(_Validator):

    def __init__(self, constants):
        self._constants = tuple(constants)

    def validate(self, value):
        if value not in self._constants:
            raise ValueError, "Incorrect value(s), possible values: " + str(self._constants)
        return value

class LengthValidator(_Validator):

    def __init__(self, length):
        self._length = length

    def validate(self, value):
        if len(value) != self._length:
            raise ValueError, "Value must be of length %i." % self._length
        return value

class CastValidator(_Validator):
    
    def __init__(self, cls):
        self._cls = cls
    
    def validate(self, value):
        if isinstance(value, Mapping):
            return self._cls(**value)
        elif isinstance(value, Iterable):
            return self._cls(*value)
        else:
            return self._cls(value)

def iter_parameters(obj):
    for name, parameter in getattr(obj, '__parameters__', {}).iteritems():
        wrapper = obj.__dict__.get(name, [])

        for value in wrapper:
            for x in iter_parameters(value):
                yield x

        yield obj, name, parameter

def iter_values(obj, keep_frozen=True):
    for baseobj, name, parameter in iter_parameters(obj):
        try:
            wrapper = parameter._get_wrapper(baseobj)
        except AttributeError: # No value
            continue
    
        if wrapper.is_frozen() and not keep_frozen:
            continue

        for value in wrapper:
            if hasattr(value, '__parameters__'):
                continue
            yield baseobj, name, value

def freeze(obj):
    for baseobj, name, parameter in iter_parameters(obj):
        wrapper = baseobj.__dict__.get(name)
        if not wrapper: # Create empty wrapper to be frozen
            baseobj.__dict__[name] = _ParameterValuesWrapper(())
        parameter.freeze(baseobj)

def expand(obj):
    obj = copy.deepcopy(obj)

    prm_values = {}
    baseobj_ids = {}
    for baseobj, _name, parameter in iter_parameters(obj):
        try:
            wrapper = parameter._get_wrapper(baseobj)
        except AttributeError: # No value
            continue

        if wrapper.is_frozen():
            continue

        baseobj_id = id(baseobj) # Use id in case baseobj is not hashable
        prm_values[(baseobj_id, parameter)] = list(wrapper)
        baseobj_ids[baseobj_id] = baseobj

    combinations, names, _varied = combine(prm_values)
    baseobjs = map(baseobj_ids.get, map(itemgetter(0), names))
    parameters = map(itemgetter(1), names)

    objs = []
    for combination in combinations:
        for baseobj, parameter, value in zip(baseobjs, parameters, combination):
            parameter.__set__(baseobj, value)
        objs.append(copy.deepcopy(obj))

    return objs
