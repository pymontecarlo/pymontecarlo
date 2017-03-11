#!/usr/bin/env python
"""
Base class for HDF5 handlers
"""

# Standard library modules.
import abc

# Third party modules.

import numpy as np

# Local modules.
from pymontecarlo import iter_hdf5handlers

# Globals and constants variables.

def find_parse_hdf5handler(group):
    for handler in iter_hdf5handlers():
        if handler.can_parse(group):
            return handler
    raise ValueError("No handler found")

def find_convert_hdf5handler(obj, group):
    for handler in iter_hdf5handlers():
        if handler.can_convert(obj, group):
            return handler
    raise ValueError("No handler found")

class HDF5Handler(object):

    CLASS = None
    VERSION = 1

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
