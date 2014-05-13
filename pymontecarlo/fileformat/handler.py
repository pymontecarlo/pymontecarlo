#!/usr/bin/env python
"""
================================================================================
:mod:`handler` -- Base class for handlers
================================================================================

.. module:: handler
   :synopsis: Base class for handlers

.. inheritance-diagram:: pymontecarlo.handler

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.
from pkg_resources import iter_entry_points

# Local modules.

# Globals and constants variables.

def find_parse_handler(handler_name, *args, **kwargs):
    for entry_point in iter_entry_points(handler_name):
        handler = entry_point.load()()
        if handler.can_parse(*args, **kwargs):
            return handler
    raise ValueError("No handler found")

def find_convert_handler(handler_name, *args, **kwargs):
    for entry_point in iter_entry_points(handler_name):
        handler = entry_point.load()()
        if handler.can_convert(*args, **kwargs):
            return handler
    raise ValueError("No handler found")

class _Handler(object):

    CLASS = None

    def can_parse(self, source, *args, **kwargs):
        raise NotImplementedError

    def parse(self, source, *args, **kwargs):
        return self.CLASS()

    def _parse_handlers(self, handler_name, *args, **kwargs):
        return find_parse_handler(handler_name, *args, **kwargs).parse(*args, **kwargs)

    def can_convert(self, obj, *args, **kwargs):
        return isinstance(obj, self.CLASS)

    def convert(self, obj, *args, **kwargs):
        raise NotImplementedError

    def _convert_handlers(self, handler_name, *args, **kwargs):
        return find_convert_handler(handler_name, *args, **kwargs).convert(*args, **kwargs)
