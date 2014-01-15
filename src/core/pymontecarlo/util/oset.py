#!/usr/bin/env python
"""
================================================================================
:mod:`oset` -- Ordered set
================================================================================

.. module:: oset
   :synopsis: Ordered set

.. inheritance-diagram:: pymontecarlo.util.oset

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from collections import MutableSet, MutableSequence

# Third party modules.

# Local modules.

# Globals and constants variables.

class oset(MutableSet, MutableSequence):

    def __init__(self, iterable=None):
        self._sequence = []
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return self._sequence.__len__()

    def __contains__(self, key):
        return key in self._sequence

    def __delitem__(self, value):
        self._sequence.__delitem__(value)

    def __iter__(self):
        return iter(self._sequence)

    def __reversed__(self):
        return self._sequence.__reversed__()

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, oset):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)

    def __del__(self):
        self.clear() # remove circular references

    def __getitem__(self, index):
        return self._sequence.__getitem__(index)

    def __setitem__(self, index, value):
        if value not in self._sequence:
            self._sequence.__setitem__(index, value)
        else:
            raise ValueError("Set already contains value (%s)" % value)

    def add(self, value):
        if value not in self._sequence:
            self._sequence.append(value)
        else:
            raise ValueError("Set already contains value (%s)" % value)

    def insert(self, index, value):
        if value not in self._sequence:
            self._sequence.insert(index, value)
        else:
            raise ValueError("Set already contains value (%s)" % value)

    def discard(self, value):
        self._sequence.remove(value)
