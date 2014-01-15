#!/usr/bin/env python
"""
================================================================================
:mod:`histogram` -- Histogram to store data from simulations
================================================================================

.. module:: histogram
   :synopsis: Histogram to store data from simulations

.. inheritance-diagram:: pymontecarlo.util.histogram

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import sys
import bisect

# Third party modules.
import numpy as np

# Local modules.

# Globals and constants variables.

class _Histogram:
    """
    Abstract class common to all histograms.
    """

    def __init__(self, bins):
        """
        Creates a new histogram. A histogram is used to store data in bins.

        :arg bins: first value of each bin.
            The last bin is used as an overflow for values greater or equal to
            its value.
        :type bins: :class:`list`
        """
        self._bins = sorted(bins)
        self._values = np.zeros(len(bins) + 1) # + 1 for underflow

    def __repr__(self):
        steps = len(self._bins)
        minvalue = self._bins[0]
        maxvalue = self._bins[-1]

        return "Histogram(min=%s, max=%s, bins=%i)" % (minvalue, maxvalue, steps)

    def __iter__(self):
        return zip([float('-inf')] + self._bins, self._values)

    def __iadd__(self, other):
        if self._bins != other._bins:
            raise ValueError("Histogram have different bins")

        self._values += other._values
        return self

    def _bin(self, binvalue):
        """
        Returns the index of the bin which contains the specified value.
        """
        return bisect.bisect_right(self._bins, binvalue)

    def _pprint(self, values, stream=None):
        """
        Prints in a tabulated format the bins and their value.
        """
        if stream is None:
            stream = sys.stdout

        ranges = ["< %s" % self._bins[0]]
        ranges += ["[%s, %s[" % (self._bins[i], self._bins[i + 1]) \
                                    for i in range(len(self._bins) - 1)]
        ranges.append(">= %s" % self._bins[-1])

        length = max(len(r) for r in ranges)

        for i, r in enumerate(ranges):
            stream.write("%s\t%s\n" % (r.rjust(length), values[i]))

    def clear(self):
        """
        Clears all values.
        """
        self._values[:] = 0.0

    @property
    def bins(self):
        """
        Returns the bins.
        Each value corresponds to the lower limit of each bin.
        """
        return np.array([float('-inf')] + self._bins)

class CountHistogram(_Histogram):
    """
    Histogram to count the number of times a value appears.
    """

    def pprint(self, stream=None):
        self._pprint(self.counts, stream)

    def add(self, binvalue):
        """
        Adds a count to the specified bin.

        :arg binvalue: value of the bin
        """
        self._values[self._bin(binvalue)] += 1

    @property
    def counts(self):
        """
        Number of counts.

        The first value of the array is the underflow and the last one is the
        overflow.
        """
        return self._values

class SumHistogram(_Histogram):
    """
    Histogram to sum the values in bins.
    The sum of squares in also recorded.
    """

    def __init__(self, bins):
        _Histogram.__init__(self, bins)

        self._squares = np.zeros(len(bins) + 1) # + 1 for underflow

    def __iter__(self):
        return zip([float('-inf')] + self._bins, self._values, self._squares)

    def __iadd__(self, other):
        _Histogram.__iadd__(self, other)
        self._squares += other._squares
        return self

    def clear(self):
        _Histogram.clear(self)
        self._squares[:] = 0.0

    def pprint(self, stream=None):
        self._pprint(self.sums, stream)

    def add(self, binvalue, value):
        """
        Adds the specified value to the specified bin.

        :arg binvalue: value of the bin
        :arg value: value to add to the bin
        """
        b = self._bin(binvalue)
        self._values[b] += value
        self._squares[b] += value ** 2

    @property
    def sums(self):
        """
        Returns the value of each bin.
        The values correspond to the sum of the values added.

        The first value of the array is the underflow and the last one is the
        overflow.
        """
        return self._values

    @property
    def squares(self):
        """
        Return the sum of squares of each bin.
        The values correspond to the sum of the square value added.

        The first value of the array is the underflow and the last one is the
        overflow.
        """
        return self._squares
