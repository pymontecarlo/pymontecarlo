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
from collections import MutableSet, MutableMapping, MutableSequence, Mapping, Iterable
import copy
from operator import itemgetter
import inspect

# Third party modules.

# Local modules.
from pymontecarlo.util.multipleloop import combine

# Globals and constants variables.

class ParameterizedMetaClass(type):
    """
    Meta class that automatically registered parameters defined in the class
    header.
    """

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
    """
    Class where values of parameters are saved. 
    This wrapper is required to allow single or list of values to be retrieved
    and to freeze the modification of values.
    """

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
        """
        Returns a list of values if more than one value is defined, or a single
        value is only one value is defined.
        """
        if len(self._values) == 1:
            return self._values[0]
        else:
            return list(self._values)

    def get_list(self):
        """
        Returns a list of values.
        """
        return list(self._values)

    def freeze(self):
        """
        Disables the modification of the values.
        """
        self._frozen = True

    def is_frozen(self):
        """
        Returns whether the values can be modified.
        """
        return self._frozen

_PASS_WRAPPER = _ParameterValuesWrapper(())

class Parameter(object):

    def __init__(self, validators=None, doc=None):
        """
        Creates a new parameter.
        The name of the parameter is defined by the variable this object
        will point to.
        The values assigned to this parameter are validated using the
        specified validators.
        
        :arg validators: list of :class:`_Validator` derived classes 
            that ensures that the value(s) entered are valid.
        :arg doc: documentation of this parameter
        """
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
        if obj is None:
            return self
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

class FrozenParameter(Parameter):

    def __init__(self, klass_or_value, doc=None, args=(), kwargs=None):
        """
        Creates a frozen parameter.
        Either the frozen value of this parameter should be specified, or
        a class which will be instantiated when the parameter is first 
        retrieved.
        
        :arg klass_or_value: frozen class or value
        :arg doc: documentation
        :arg args: arguments to be passed to the class during instantiation
        :arg kwargs: keyword-arguments to be passed to the class 
            during instantiation
        """
        Parameter.__init__(self, None, doc)

        self._value = klass_or_value
        self._klass_args = args
        if kwargs is None: kwargs = {}
        self._klass_kwargs = kwargs

    def _get_wrapper(self, obj, objtype=None):
        if not obj.__dict__.has_key(self.name):
            value = self._value
            if inspect.isclass(value):
                value = self._value(*self._klass_args, **self._klass_kwargs)
            wrapper = _ParameterValuesWrapper([value])
            wrapper.freeze()
            obj.__dict__[self.name] = wrapper
        return obj.__dict__[self.name]

    def __set__(self, obj, values):
        raise AttributeError, "Frozen parameter (%s)" % self._name

class ParameterAlias(object):

    def __init__(self, alias, doc=None):
        """
        Creates an alias of a parameter.
        If the value of the alias is modified, the value of the original
        parameter will also be modified.
        
        :arg alias: original parameter
        :arg doc: documentation
        """
        self._alias = alias
        self.__doc__ = doc

    def __repr__(self):
        return '<%s(%s)>' % (self.__class__.__name__, self._alias.name)

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
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
        for parameter in self.__parameters__.values():
            yield parameter.__get__(self)

    def __contains__(self, item):
        return self._get_key(item) in self.__parameters__

    def __deepcopy__(self, memo):
        # Override
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            result.__dict__[k] = copy.deepcopy(v, memo)

        # Key must be update with new key from objects
        for key, parameter in result.__parameters__.items():
            wrapper = result.__dict__[key]
            newkey = self._get_key(wrapper.get())

            del result.__parameters__[key]
            parameter._name = newkey
            result.__parameters__[newkey] = parameter

            del result.__dict__[key]
            result.__dict__[newkey] = wrapper

        return result

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
            raise KeyError, key
        del self.__parameters__[key]
        del self.__dict__[key]

class ParameterizedMutableSequence(MutableSequence):

    def __init__(self, validators=None):
        self._validators = validators
        self.__parameters__ = {}

    def __repr__(self):
        valstr = ', '.join(map(str, self))
        return '<%s(%s)>' % (self.__class__.__name__, valstr)

    def __len__(self):
        return len(self.__parameters__)

    def __iter__(self):
        for index in range(len(self.__parameters__)):
            key = self._get_key(index)
            parameter = self.__parameters__[key]
            yield parameter.__get__(self)

    def __contains__(self, value):
        return value in list(self)

    def __getitem__(self, s):
        isslice = True
        if not isinstance(s, slice):
            s = slice(s, s + 1)
            isslice = False

        values = []
        for index in range(*s.indices(len(self.__parameters__))):
            key = self._get_key(index)
            if key not in self.__parameters__:
                raise IndexError, index
            parameter = self.__parameters__[key]
            values.append(parameter.__get__(self))

        if not isslice:
            return values[0]
        return values

    def __setitem__(self, index, value):
        key = self._get_key(index)
        if key not in self.__parameters__:
            raise IndexError, index
        parameter = self.__parameters__[key]
        parameter.__set__(self, value)

    def __delitem__(self, s):
        if not isinstance(s, slice):
            s = slice(s, s + 1)

        for index in range(*s.indices(len(self.__parameters__))):
            key = self._get_key(index)
            if key not in self.__parameters__:
                raise IndexError, index
            del self.__parameters__[key]
            del self.__dict__[key]

    def _get_key(self, index):
        return 'item%i' % index

    def insert(self, index, value):
        # Shift
        for i in reversed(range(index, len(self.__parameters__))):
            oldkey = self._get_key(i)
            newkey = self._get_key(i + 1)

            self.__parameters__[newkey] = self.__parameters__[oldkey]
            self.__parameters__[newkey]._name = newkey
            del self.__parameters__[oldkey]

            self.__dict__[newkey] = self.__dict__[oldkey]
            del self.__dict__[oldkey]

        # Insert new value
        key = self._get_key(index)

        parameter = Parameter(self._validators)
        parameter._name = key
        self.__parameters__[key] = parameter
        parameter.__set__(self, value)

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
            raise KeyError, key
        return self.__parameters__[key].__get__(self)

    def __delitem__(self, key):
        if key not in self.__parameters__:
            raise KeyError, key
        del self.__dict__[key]
        del self.__parameters__[key]

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
    """
    Automatically defined two parameters to specified an angle value in
    radians or degrees::
    
        class Object(object):
            
            __metaclass__ = ParameterizedMetaClass
            
            angle = AngleParameter()
        
        obj = Object()
        obj.angle_rad = math.pi
        print obj.angle_deg # 180.0
    
    """
    
    def _new(self, cls, clsname, bases, methods, name):
        parameter = methods.pop(name)
        methods[name + '_rad'] = parameter
        methods[name + '_deg'] = FactorParameterAlias(parameter, math.pi / 180.0)
        Parameter._new(self, cls, clsname, bases, methods, name + '_rad')

class UnitParameter(Parameter):
    """
    Automatically defined all possible unit prefix (M, k, d, etc.) for 
    a quantity::
    
        class Object(object):
            
            __metaclass__ = ParameterizedMetaClass
            
            distance = UnitParameter('m')
        
        obj = Object()
        obj.distance_cm = 156
        print obj.distance_m # 1.56
    """
    
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
    """
    Automatically defined all possible time prefix (s, min, hr, etc.) for 
    a quantity::
    
        class Object(object):
            
            __metaclass__ = ParameterizedMetaClass
            
            duration = TimeParameter()
        
        obj = Object()
        obj.duration_s = 78
        print obj.duration_min # 1.3
    """

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
        """
        Raises a :exc:`ValueError` if the value is not valid.
        The methods must return the value.
        """
        raise NotImplementedError

class PassValidator(_Validator):
    """
    Pass validator. Value is always valid.
    """

    def validate(self, value):
        return value

class SimpleValidator(_Validator):

    def __init__(self, func, message=None):
        """
        Function validator.
        
        :arg func: function that returns ``True`` if the value is valid.
            The function takes only one argument, the value.
        :arg message: message to be passed to the exception if the value
            is not valid
        """
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
        """
        Validates that the value is within the specified constant values.
        
        :arg constants: constant values
        """
        self._constants = tuple(constants)

    def validate(self, value):
        if value not in self._constants:
            raise ValueError, "Incorrect value(s), possible values: " + str(self._constants)
        return value

class LengthValidator(_Validator):

    def __init__(self, length):
        """
        Validates the length of the value.
        
        :arg length: required length of the value
        """
        self._length = length

    def validate(self, value):
        if len(value) != self._length:
            raise ValueError, "Value must be of length %i." % self._length
        return value

class CastValidator(_Validator):
    
    def __init__(self, cls):
        """
        Casts the specified class to the value.
        """
        self._cls = cls
    
    def validate(self, value):
        if isinstance(value, Mapping):
            return self._cls(**value)
        elif isinstance(value, Iterable) and not isinstance(value, basestring):
            return self._cls(*value)
        else:
            return self._cls(value)

def iter_parameters(obj):
    """
    Recursively iterates over all parameters defined in the specified object.
    The method yields:
    
        * the name of the parameter
        * the parameter object
        * the object contains the parameter
        
    :arg obj: object containing parameters
    """
    for name, parameter in getattr(obj, '__parameters__', {}).iteritems():
        wrapper = obj.__dict__.get(name, [])

        for value in wrapper:
            for x in iter_parameters(value):
                yield x

        yield name, parameter, obj

def iter_values(obj, keep_frozen=True):
    """
    Recursively iterates over all values defined for all parameters in the
    specified object.
    The method yields:
    
        * the object from which the value belongs
        * the name of the parameter with this value
        * the value
    
    :arg obj: object containing parameters
    :arg keep_frozen: whether to return frozen values
    """
    for name, parameter, baseobj in iter_parameters(obj):
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
    """
    Recursively freezes all parameters in the specified object.
    
    :arg obj: object containing parameters
    """
    for name, parameter, baseobj in iter_parameters(obj):
        wrapper = baseobj.__dict__.get(name)
        if not wrapper: # Create empty wrapper to be frozen
            baseobj.__dict__[name] = _ParameterValuesWrapper(())
        parameter.freeze(baseobj)

class Expander(object):
    """
    Expands an parameterized object based on all possible combinations of
    paramter/values.
    """

    def expand(self, obj):
        """
        Returns a list of the specified object where only one value is defined
        for each parameter.
        The function computes all possible combinations of parameter/values.
        
        :arg obj: object containing parameters
        """
        obj = copy.deepcopy(obj)

        parameter_values, parameter_obj_ids = \
            self._create_parameter_values_dict(obj)

        combinations, parameter_objs, parameters = \
            self._create_combinations(parameter_values, parameter_obj_ids)

        objs = self._create_objects(obj, combinations, parameter_objs, parameters)

        return objs

    def _create_parameter_values_dict(self, obj):
        parameter_values = {}
        parameter_obj_ids = {}
        for _name, parameter, parameter_obj in iter_parameters(obj):
            try:
                wrapper = parameter._get_wrapper(parameter_obj)
            except AttributeError: # No value
                continue

            if wrapper.is_frozen():
                continue

            if len(wrapper) < 2:
                continue

            parameter_obj_id = id(parameter_obj) # Use id in case baseobj is not hashable
            parameter_values[(parameter_obj_id, parameter)] = list(wrapper)
            parameter_obj_ids[parameter_obj_id] = parameter_obj

        return parameter_values, parameter_obj_ids

    def _create_combinations(self, parameter_values, parameter_obj_ids):
        combinations, names, _varied = combine(parameter_values)
        parameter_objs = map(parameter_obj_ids.get, map(itemgetter(0), names))
        parameters = map(itemgetter(1), names)

        return combinations, parameter_objs, parameters

    def _create_objects(self, baseobj, combinations, parameter_objs, parameters):
        objs = []
        for combination in combinations:
            for parameter_obj, parameter, value in zip(parameter_objs, parameters, combination):
                parameter.__set__(parameter_obj, value)
            objs.append(copy.deepcopy(baseobj))
    
        return objs

_root_expander = Expander()
expand = _root_expander.expand
