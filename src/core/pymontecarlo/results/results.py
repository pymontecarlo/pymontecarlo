#!/usr/bin/env python
"""
================================================================================
:mod:`results` -- Container of all results
================================================================================

.. module:: results
   :synopsis: Container of all results

.. inheritance-diagram:: pymontecarlo.output.results

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

__all__ = ['Results']

# Standard library modules.
from collections import Mapping, Sequence

# Third party modules.

# Local modules.
from pymontecarlo.util.parameter import freeze

# Globals and constants variables.

class ResultsContainer(Mapping):

    def __init__(self, options, results={}):
        """
        Internal container for the results.

        :arg options: options used to generate these results
        :type options: :class:`Options`

        :arg results: results to be part of this container.
            The results are specified by a key (key of the detector) and a
            :class:`Result <pymontecarlo.result.base.result.Result>` class.
        :type results: :class:`dict`
        """
        self._options = options
        freeze(self._options)

        self._results = {}
        for key, result in results.items():
            if key not in options.detectors:
                raise KeyError('No detector found for result %s' % key)
            self._results[key] = result

    def __repr__(self):
        return '<%s(%s)>' % (self.__class__.__name__,
                             ', '.join(self._results.keys()))

    def __len__(self):
        return len(self._results)

    def __getitem__(self, key):
        return self._results[key]

    def __iter__(self):
        return iter(self._results)

    @property
    def options(self):
        return self._options

class Results(Sequence):
    """
    :class:`.ResultsSequence` is a container of several :class:`.Results`.
    It preserves the order of the results.

    The class works like an immutable :class:`list` object.

    The class also contains parameter values associated to each results.
    The parameters are saved in a dictionary for each results.
    Note that results can have different parameters.
    Parameters are immutable; they cannot be modified.
    Parameters can be retrieved using the property :attr:`parameters`::

        >>> results_seq.parameters[0]['param1']
        >>> 2.0
    """

    def __init__(self, options, results):
        self._options = options
        freeze(self._options)

        self._list_results = []
        for container in results:
            if not isinstance(container, ResultsContainer):
                container = ResultsContainer(*container)
            self._list_results.append(container)

    def __repr__(self):
        return '<%s(%i results)>' % (self.__class__.__name__, len(self))

    def __len__(self):
        return len(self._list_results)

    def __getitem__(self, index):
        return self._list_results[index]

    @property
    def options(self):
        return self._options

