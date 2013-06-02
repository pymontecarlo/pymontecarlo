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

# Third party modules.

# Local modules.

# Globals and constants variables.

class ParameterizedMetaClass(type):

    def __new__(cls, clsname, bases, methods):
        # Attach attribute names to parameters
        parameters = {}
        for key, value in methods.items():
            if isinstance(value, Parameter):
                value._new(cls, clsname, bases, methods, key)
                parameters[value.name] = value

        # Add __parameters__ attribute
        methods['__parameters__'] = parameters

        return type.__new__(cls, clsname, bases, methods)

class _ValueWrapper(object):

    def __init__(self, values):
        self._values = values
        self._frozen = False

    def get(self):
        if len(self._values) == 1:
            return self._values[0]
        else:
            return self._values

    def freeze(self):
        self._frozen = True

    def is_frozen(self):
        return self._frozen

_PassValueWrapper = _ValueWrapper(())

class Parameter(object):

    def __init__(self, validator=None, doc=None):
        self._name = None
        self.__doc__ = doc

        if validator is None:
            validator = PassValidator()
        self._validator = validator

    def __repr__(self):
        return '<%s(%s)>' % (self.__class__.__name__, self.name)

    def __get__(self, obj, objtype=None):
        if not obj.__dict__.has_key(self.name):
            raise AttributeError, "No value"

        wrapper = obj.__dict__[self.name]
        return wrapper.get()

    def __set__(self, obj, values):
        if obj.__dict__.get(self.name, _PassValueWrapper).is_frozen():
            raise AttributeError, "Frozen parameter"

        if not isinstance(values, list):
            values = (values,)

        for value in values:
            self._validator.validate(value)

        obj.__dict__[self.name] = _ValueWrapper(values)

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
        return self._alias.__get__(obj, objtype)

    def __set__(self, obj, value):
        self._alias.__set__(obj, value)

class AngleDegParameterAlias(ParameterAlias):

    def __get__(self, obj, objtype=None):
        values = ParameterAlias.__get__(self, obj, objtype)

        if isinstance(values, tuple):
            return tuple(map(math.degrees, values))
        else:
            return math.degrees(values)

    def __set__(self, obj, values):
        if not isinstance(values, list):
            values = (values,)
        values = map(math.radians, values)
        ParameterAlias.__set__(self, obj, values)

class AngleParameter(Parameter):

    def _new(self, cls, clsname, bases, methods, name):
        parameter = methods.pop(name)
        methods[name + '_rad'] = parameter
        methods[name + '_deg'] = AngleDegParameterAlias(parameter)
        Parameter._new(self, cls, clsname, bases, methods, name + '_rad')

class _Validator(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def validate(self, value):
        raise NotImplementedError

class PassValidator(_Validator):

    def validate(self, value):
        pass

class SimpleValidator(_Validator):

    def __init__(self, func, message=None):
        if not callable(func):
            raise ValueError, "Validation function must be callable"
        self._func = func
        self._message = message

    def validate(self, value):
        if not self._func(value):
            raise ValueError, self._message or "Invalid value"

class EnumValidator(_Validator):

    def __init__(self, constants):
        self._constants = tuple(constants)

    def validate(self, value):
        if value not in self._constants:
            raise ValueError, "Incorrect value, possible values: " + str(self._constants)

class LengthValidator(_Validator):

    def __init__(self, length):
        self._length = length

    def validate(self, value):
        if len(value) != self._length:
            raise ValueError, "Value must be of length %i." % self._length

def freeze(obj):
    for parameter in obj.__parameters__.itervalues():
        parameter.freeze(obj)

#class Test(object):
#
#    __metaclass__ = ParameterizedMetaClass
#
#    x = Parameter(5.0, doc='x parameter')
#    y = AngleParameter(6.0)
#
#class Test2(object):
#
#    __metaclass__ = ParameterizedMetaClass
#
#    a = Parameter(5.0, doc='x parameter')
#
#class Test3(object):
#
#    __metaclass__ = ParameterizedMetaClass
#
#    h = Parameter(5.0, doc='x parameter')
#
#test1 = Test()
#test2 = Test2()
#test3 = Test3()
#test4 = Test3()
##print map(id, test1.__parameters__)
##print map(id, test2.__parameters__)
##
#test1.x = test2
#test2.a = [test3, test4]
#test3.h = [1999, 20001]
##print test1.x, test2.x
#
#for s in walk(test1):
#    print s


#for parameter in test.__parameters__:
#    print parameter, list(iter(parameter))
#print test.__class__.__dict__
