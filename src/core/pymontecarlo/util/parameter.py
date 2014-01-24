#!/usr/bin/env python
"""
================================================================================
:mod:`option` -- Building block for options
================================================================================

.. module:: option
   :synopsis: Building block for options

.. inheritance-diagram:: pymontecarlo.options.option

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import copy
import operator
from operator import itemgetter
from collections import MutableMapping, MutableSet

# Third party modules.
import numpy as np

# Local modules.
from pymontecarlo.util.multipleloop import combine

# Globals and constants variables.

class ParameterizedMetaclass(type):
    """
    Meta class that automatically registered parameters defined in the class
    header.
    """

    def __new__(cls, clsname, bases, methods):
        parameters = {}

        # Parameters from parents
        parents = [b for b in bases if isinstance(b, ParameterizedMetaclass)]
        for base in parents:
            parameters.update(base.__parameters__)

        # Attach attribute names to parameters
        for key, value in list(methods.items()):
            if not isinstance(value, Parameter):
                continue
            value._new(cls, clsname, bases, methods, key)
            parameters[value.name] = value

        # Add __parameters__ attribute
        methods['__parameters__'] = parameters

        return type.__new__(cls, clsname, bases, methods)

class Parameter(object):

    def __init__(self, dtype=object, validators=None, fields=None, doc=None):
        self._dtype = np.dtype(dtype)
        if self._dtype.hasobject:
            self._dtype = np.dtype(dtype, metadata={'class': dtype})

        if validators is None:
            validators = []
        if not hasattr(validators, '__iter__'):
            validators = [validators]
        self._validators = validators

        if fields is not None and len(fields) == 0:
            raise ValueError('At least one field must be specified')
        if fields is None:
            fields = []
        self._fields = fields

        self.__doc__ = doc

    def __repr__(self):
        return '<%s(%s)>' % (self.__class__.__name__, self.name)

    def __get__(self, obj, objtype=None, simplify=True):
        if obj is None:
            return self
        if self.name not in obj.__dict__:
            raise AttributeError("No value for attribute '%s'" % self.name)

        values = obj.__dict__[self.name]

        if simplify:
            values = self._simplify_values(values)

        return values

    def __set__(self, obj, values):
        if not obj.__dict__.get(self.name, np.array([])).flags.writeable:
            raise ValueError("Frozen parameter")

        # Hack when values are numpy record
        if hasattr(values, 'tolist'):
            values = values.tolist()

        # Generate 2d array
        # One value per row, each column corresponds to a field
        values = np.array(values, dtype=self._dtype, ndmin=2)

        # Check dtype for object
        if self._dtype.hasobject:
            klass = self._dtype.metadata['class']
            for value in values.flat:
                if not isinstance(value, klass):
                    raise ValueError("Wrong type of values: '%s' != '%s'" % \
                                     (value.__class__.__name__, klass.__name__))

        # Reshape values to have one value per row
        try:
            values = values.reshape((-1, len(self._fields) or 1))
        except:
            raise ValueError('Inconsistent number of values. ' + \
                             'Expected %i number per value' % len(self._fields))

        # Create recarray if fields are defined
        if self.has_field():
            dtype = [(field, values.dtype) for field in self._fields]
            values = np.rec.fromarrays(values.transpose(), dtype)

        # Validate
        self._validate(self._simplify_values(values))

        obj.__dict__[self.name] = values

    def _new(self, cls, clsname, bases, methods, name):
        self._name = name

    def _simplify_values(self, values):
        if values.size == 1:
            return next(values.flat)

        if not self.has_field():
            return values[:, 0]
        else:
            if len(values) == 1:
                return values[0]
            else:
                return values

    def _validate(self, values):
        if not hasattr(values, '__iter__'):
            values = [values]
        for value in values:
            for validator in self._validators:
                validator(value)

    def freeze(self, obj):
        if self.name not in obj.__dict__:
            obj.__dict__[self.name] = np.array([])

        obj.__dict__[self.name].flags.writeable = False

    def has_field(self):
        return len(self._fields) > 0

    @property
    def name(self):
        return self._name

class Alias(object):

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
        return '<%s(Alias of %s)>' % (self.__class__.__name__, self._alias.name)

    def __get__(self, obj, objtype=None, simplify=True):
        if obj is None:
            return self
        return self._alias.__get__(obj, objtype, simplify)

    def __set__(self, obj, value):
        self._alias.__set__(obj, value)

    def has_field(self):
        return self._alias.has_field()

    def freeze(self, obj):
        self._alias.freeze(obj)

# class FrozenParameter(Parameter):
#
#     def __init__(self, klass_or_value, doc=None, args=(), kwargs=None):
#         """
#         Creates a frozen parameter.
#         Either the frozen value of this parameter should be specified, or
#         a class which will be instantiated when the parameter is first
#         retrieved.
#
#         :arg klass_or_value: frozen class or value
#         :arg doc: documentation
#         :arg args: arguments to be passed to the class during instantiation
#         :arg kwargs: keyword-arguments to be passed to the class
#             during instantiation
#         """
#         Parameter.__init__(self, None, doc)
#
#         self._value = klass_or_value
#         self._klass_args = args
#         if kwargs is None: kwargs = {}
#         self._klass_kwargs = kwargs
#
#     def __get__(self, obj, objtype=None):
#         if obj is None:
#             return self
#
#         if not self.name in obj.__dict__:
#             value = self._value
#             if inspect.isclass(value):
#                 value = self._value(*self._klass_args, **self._klass_kwargs)
#             self._validate(value)
#             obj.__dict__[self.name] = {'value': value, 'frozen': True}
#
#         return Parameter.__get__(self, obj, objtype=objtype)

class FactorAlias(Alias):
    """
    Multiplies the set value(s) by the specified factor before passing them
    to the alias parameter and divides the returned value(s) from the
    alias parameter by the specified factor.
    """

    def __init__(self, alias, factor):
        Alias.__init__(self, alias)
        self._factor = factor

    def __get__(self, obj, objtype=None, simplify=True):
        values = Alias.__get__(self, obj, objtype, False)

        # Hack since record and recarray do not have ufunc
        if isinstance(values, np.rec.recarray):
            tmpvalues = values.view((self._alias._dtype, len(values.dtype.names))) / self._factor
            values = np.rec.fromarrays(tmpvalues.transpose(), values.dtype)
        else:
            values = values / self._factor

        if simplify:
            values = self._alias._simplify_values(values)

        return values

    def __set__(self, obj, values):
        values = np.array(values) * self._factor
        Alias.__set__(self, obj, values)
#
class AngleParameter(Parameter):
    """
    Automatically defined two parameters to specified an angle value in
    radians or degrees::

        class Object(object, metaclass=OptionMetaclass):
            angle = AngleParameter()

        obj.angle_rad = math.pi
        print obj.angle_deg # 180.0

    """

    def __init__(self, validators=None, fields=None, doc=None):
        Parameter.__init__(self, np.float, validators, fields, doc)

    def _new(self, cls, clsname, bases, methods, name):
        parameter = methods.pop(name)
        methods[name + '_rad'] = parameter
        methods[name + '_deg'] = FactorAlias(parameter, np.pi / 180.0)
        Parameter._new(self, cls, clsname, bases, methods, name + '_rad')

class UnitParameter(Parameter):
    """
    Automatically defined all possible unit prefix (M, k, d, etc.) for
    a quantity::

        class Object(object, metaclass=OptionMetaclass):
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

    def __init__(self, unit, validators=None, fields=None, doc=None):
        Parameter.__init__(self, float, validators, fields, doc)
        self._unit = unit

    def _new(self, cls, clsname, bases, methods, name):
        parameter = methods.pop(name)
        methods[name + '_' + self._unit] = parameter

        for prefix, factor in self._prefix.items():
            methods['%s_%s%s' % (name, prefix, self._unit)] = \
                FactorAlias(parameter, factor)

        Parameter._new(self, cls, clsname, bases, methods, name + "_" + self._unit)

class TimeParameter(Parameter):
    """
    Automatically defined all possible time prefix (s, min, hr, etc.) for
    a quantity::

        class Object(object, metaclass=OptionMetaclass):
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

    def __init__(self, validators=None, fields=None, doc=None):
        Parameter.__init__(self, np.float, validators, fields, doc)

    def _new(self, cls, clsname, bases, methods, name):
        parameter = methods.pop(name)

        for unit, factor in self._factors.items():
            methods['%s_%s' % (name, unit)] = \
                FactorAlias(parameter, factor)

        Parameter._new(self, cls, clsname, bases, methods, name + '_s')

def range_validator(low=-np.infty, high=np.infty, inclusive=True):
    """
    Validates if a value is between the low and high limits, inclusively.
    """
    if inclusive:
        op1 = operator.lt
        op2 = operator.gt
    else:
        op1 = operator.le if not np.isinf(low) else operator.lt
        op2 = operator.ge if not np.isinf(high) else operator.gt

    op1str = '[' if op1.__name__ == 'lt' else ']'
    op2str = ']' if op2.__name__ == 'gt' else '['

    def validator(value):
        if op1(value, low) or op2(value, high):
            raise ValueError('Value (%s) must be between %s%s, %s%s' % \
                             (value, op1str, low, high, op2str))

    return validator

def notempty_validator():
    """
    Validates if a value is not empty or not None.
    """
    def validator(value):
        if value is None or not bool(value):
            raise ValueError('Empty value or None')
    return validator

def enum_validator(constants):
    """
    Validates that the value is within the specified constant values.

    :arg constants: constant values
    """
    constants = frozenset(constants)
    def validator(value):
        if value not in constants:
            raise ValueError("Incorrect value(s), possible values: " + str(constants))
    return validator

class ParameterizedMutableMapping(MutableMapping):

    def __init__(self, *parameter_args, **parameter_kwargs):
        self._parameter_args = parameter_args
        self._parameter_kwargs = parameter_kwargs
        self.__parameters__ = {}

    def __repr__(self):
        valstr = ', '.join(['%s: %s' % item for item in self.items()])
        return '<%s(%s)>' % (self.__class__.__name__, valstr)

    def __str__(self):
        return str(dict(self))

    def __len__(self):
        return len(self.__parameters__)

    def __getitem__(self, key):
        if key not in self.__parameters__:
            raise KeyError(key)
        return self.__parameters__[key].__get__(self)

    def __delitem__(self, key):
        if key not in self.__parameters__:
            raise KeyError(key)
        del self.__dict__[key]
        del self.__parameters__[key]

    def __setitem__(self, key, value):
        try:
            parameter = self.__parameters__[key]
        except KeyError:
            parameter = Parameter(*self._parameter_args, **self._parameter_kwargs)
            parameter._name = key
            self.__parameters__[key] = parameter

        parameter.__set__(self, value)

    def __iter__(self):
        return iter(self.__parameters__)

class ParameterizedMutableSet(MutableSet):

    def __init__(self, *parameter_args, **parameter_kwargs):
        self._parameter_args = parameter_args
        self._parameter_kwargs = parameter_kwargs
        self.__parameters__ = {}

    def __repr__(self):
        valstr = ', '.join(map(str, self))
        return '<%s(%s)>' % (self.__class__.__name__, valstr)

    def __str__(self):
        return str(set(self))

    def __len__(self):
        return len(self.__parameters__)

    def __iter__(self):
        for parameter in self.__parameters__.values():
            yield parameter.__get__(self)

    def __contains__(self, item):
        return self._get_key(item) in self.__parameters__

#     def __deepcopy__(self, memo):
#          Override
#         cls = self.__class__
#         result = cls.__new__(cls)
#         memo[id(self)] = result
#         for k, v in self.__dict__.items():
#             result.__dict__[k] = copy.deepcopy(v, memo)
#
#          # Key must be update with new key from objects
#          for key, parameter in result.__parameters__.items():
#              values = parameter.__get__(self, simplify=False)
#              newkey = self._get_key(values)
#
#              del result.__parameters__[key]
#              parameter._name = newkey
#              result.__parameters__[newkey] = parameter
#
#              del result.__dict__[key]
#              result.__dict__[newkey] = values
#
#         return result

    def _get_key(self, item):
        return str(hash(item))

    def add(self, item):
        key = self._get_key(item)

        try:
            parameter = self.__parameters__[key]
        except KeyError:
            parameter = Parameter(*self._parameter_args, **self._parameter_kwargs)
            parameter._name = key
            self.__parameters__[key] = parameter

        parameter.__set__(self, item)

    def discard(self, item):
        key = self._get_key(item)
        if key not in self.__parameters__:
            raise KeyError(key)
        del self.__parameters__[key]
        del self.__dict__[key]

def iter_parameters(obj):
    """
    Recursively iterates over all parameters defined in the specified object.
    The method yields:

        * the object contains the parameter
        * the name of the parameter
        * the parameter object

    :arg obj: object containing parameters
    """
    for name, parameter in getattr(obj, '__parameters__', {}).items():
        subobj = getattr(obj, name, None)
        if subobj is not None:
            yield from iter_parameters(subobj)
        yield obj, name, parameter

def iter_values(obj):
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
    for baseobj, name, parameter in iter_parameters(obj):
        try:
            values = np.array(parameter.__get__(baseobj), ndmin=1)
        except AttributeError: # No value
            continue

        for value in values:
            if hasattr(value, '__parameters__'):
                continue
            yield baseobj, name, value

def freeze(obj):
    """
    Recursively freezes all parameters in the specified object.

    :arg obj: object containing parameters
    """
    for baseobj, _, parameter in iter_parameters(obj):
        parameter.freeze(baseobj)

class Expander(object):
    """
    Expands an parameterized object based on all possible combinations of
    parameter/values.
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
        if not parameter_values:
            return [obj]

        combinations, parameter_objs, parameters = \
            self._create_combinations(parameter_values, parameter_obj_ids)

        objs = self._create_objects(obj, combinations, parameter_objs, parameters)

        return objs

    def is_expandable(self, obj):
        parameter_values, _ = self._create_parameter_values_dict(obj)
        return bool(parameter_values)

    def _create_parameter_values_dict(self, obj):
        parameter_values = {}
        parameter_obj_ids = {}
        for parameter_obj, _name, parameter in iter_parameters(obj):
            try:
                values = parameter.__get__(parameter_obj, simplify=False)
            except AttributeError: # No value
                continue

            if values.size < 2:
                continue

            parameter_obj_id = id(parameter_obj) # Use id in case baseobj is not hashable
            parameter_values[(parameter_obj_id, parameter)] = values.tolist()
            parameter_obj_ids[parameter_obj_id] = parameter_obj

        return parameter_values, parameter_obj_ids

    def _create_combinations(self, parameter_values, parameter_obj_ids):
        combinations, names, _varied = combine(parameter_values)
        parameter_objs = list(map(parameter_obj_ids.get, map(itemgetter(0), names)))
        parameters = list(map(itemgetter(1), names))

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
