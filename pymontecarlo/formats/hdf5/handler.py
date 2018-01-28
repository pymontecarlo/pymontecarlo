#!/usr/bin/env python
"""
Base class for HDF5 handlers
"""

# Standard library modules.
import abc

# Third party modules.
import numpy as np

# Local modules.
from pymontecarlo.formats.hdf5.entrypoint import \
    find_convert_hdf5handler, find_parse_hdf5handler

# Globals and constants variables.

class HDF5HandlerBase(metaclass=abc.ABCMeta):

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
