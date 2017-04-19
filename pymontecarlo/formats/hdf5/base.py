#!/usr/bin/env python
"""
Base class for HDF5 handlers
"""

# Standard library modules.
import abc

# Third party modules.
import numpy as np

# Local modules.
from pymontecarlo.exceptions import ParseError, ConvertError
from pymontecarlo.util.entrypoint import resolve_entrypoints

# Globals and constants variables.
ENTRYPOINT_HDF5HANDLER = 'pymontecarlo.formats.hdf5'

def find_parse_hdf5handler(group):
    for clasz in resolve_entrypoints(ENTRYPOINT_HDF5HANDLER):
        handler = clasz()
        if handler.can_parse(group):
            return handler
    raise ParseError("No handler found for group: {!r}".format(group))

def find_convert_hdf5handler(obj, group):
    for clasz in resolve_entrypoints(ENTRYPOINT_HDF5HANDLER):
        handler = clasz()
        if handler.can_convert(obj, group):
            return handler
    raise ConvertError("No handler found for object {!r} and group {!r}"
                       .format(obj, group))

class HDF5Handler(object, metaclass=abc.ABCMeta):

    ATTR_CLASS = '_class'
    ATTR_VERSION = '_version'

    def _parse_hdf5handlers(self, group):
        return find_parse_hdf5handler(group).parse(group)

    def _convert_hdf5handlers(self, obj, group):
        return find_convert_hdf5handler(obj, group).convert(obj, group)

    def can_parse(self, group):
        return group.attrs.get(self.ATTR_CLASS) == np.string_(self.CLASS.__name__) and \
            group.attrs.get(self.ATTR_VERSION) == self.VERSION

    @abc.abstractmethod
    def parse(self, group):
        return self.CLASS()

    def can_convert(self, obj, group):
        return type(obj) is self.CLASS

    @abc.abstractmethod
    def convert(self, obj, group):
        group.attrs[self.ATTR_CLASS] = np.string_(self.CLASS.__name__)
        group.attrs[self.ATTR_VERSION] = self.VERSION

    @abc.abstractproperty
    def CLASS(self):
        raise NotImplementedError

    @property
    def VERSION(self):
        return 1
