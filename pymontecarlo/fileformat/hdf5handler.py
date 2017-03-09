#!/usr/bin/env python
"""
Base class for HDF5 handlers
"""

# Standard library modules.
import abc

# Third party modules.
from pkg_resources import iter_entry_points

import numpy as np

# Local modules.

# Globals and constants variables.

def find_parse_handler(handler_name, *args, **kwargs):
    for entry_point in iter_entry_points(handler_name):
        handler = entry_point.load()()
        if handler.can_parse(*args, **kwargs):
            return handler
    raise ValueError("No handler found for %s" % handler_name)

def find_convert_handler(handler_name, *args, **kwargs):
    for entry_point in iter_entry_points(handler_name):
        handler = entry_point.load()()
        if handler.can_convert(*args, **kwargs):
            return handler
    raise ValueError("No handler found for %s" % handler_name)

class HDF5Handler(object):

    CLASS = None
    VERSION = 1

    ATTR_CLASS = '_class'
    ATTR_VERSION = '_version'

    def _parse_handlers(self, handler_name, *args, **kwargs):
        return find_parse_handler(handler_name, *args, **kwargs).parse(*args, **kwargs)

    def _convert_handlers(self, handler_name, *args, **kwargs):
        return find_convert_handler(handler_name, *args, **kwargs).convert(*args, **kwargs)

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
