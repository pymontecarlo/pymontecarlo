#!/usr/bin/env python
"""
================================================================================
:mod:`convergor` -- Algorithm to check whether an iteration has converged
================================================================================

.. module:: convergor
   :synopsis: Algorithm to check whether an iteration has converged

.. inheritance-diagram:: pymontecarlo.quant.runner.convergor

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import math
import logging

# Third party modules.

# Local modules.
import pymontecarlo.util.element_properties as ep

# Globals and constants variables.

class _Convergor(object):
    def __init__(self, experimental_kratios, initial_composition, **kwargs):
        """
        Creates a new quantitative convergor.
        
        :arg experimental_kratios: experimental k-ratios for each element given 
            as a :class:`dict` where the keys are atomic numbers and the values
            are tuples of the experimental k-ratios and their uncertainties.
        :type experimental_kratios: :class:`dict`
        
        :arg initial_composition: initial composition for each element given as a 
            :class:`dict` where they keys are atomic numbers and the values
            are weight fractions.
        :type initial_composition: :class:`dict`
        """
        # Verify that each element has an experimental k-ratio
        kratios_zs = set(experimental_kratios.keys())
        composition_zs = set(initial_composition.keys())
        missing_zs = kratios_zs - composition_zs
        if missing_zs:
            symbols = map(ep.symbol, missing_zs)
            raise ValueError, 'No k-ratio found for these elements: %s' % \
                    ', '.join(symbols)

        self._experimental_kratios = dict(experimental_kratios) # copy
        self._calculated_kratios = []
        self._compositions = [dict(initial_composition)] # copy

    def __repr__(self):
        return '<%s()>' % self.__class__.__name__

    @property
    def experimental_kratios(self):
        """
        Experimental k-ratios
        """
        return self._experimental_kratios

    def add_iteration(self, kratios, composition):
        """
        Registers the results of an iteration/
        
        :arg kratios: theoretical k-ratios for each element given as a 
            :class:`dict` where the keys are atomic numbers and the values
            are tuples of the theoretical k-ratios and their uncertainties.
        :type kratios: :class:`dict`
        
        :arg composition: composition calculated for an iteration give as a 
            :class:`dict` where they keys are atomic numbers and the values
            are weight fractions.
        :type composition: :class:`dict`
        """
        self._calculated_kratios.append(kratios)
        self._compositions.append(composition)

    def has_converged(self):
        raise NotImplementedError

class _LimitConvergor(_Convergor):
    def __init__(self, experimental_kratios, initial_composition, limit, **kwargs):
        _Convergor.__init__(self, experimental_kratios, initial_composition, **kwargs)

        if limit < 0.0:
            raise ValueError, 'Limit must be greater than 0.0'
        self._limit = limit

    def __repr__(self):
        return '<%s(limit=%s)>' % (self.__class__.__name__, self.limit)

    @property
    def limit(self):
        """
        Convergence limit
        """
        return self._limit

class CompositionConvergor(_LimitConvergor):

    def has_converged(self):
        current_composition = self._compositions[-1]
        previous_composition = self._compositions[-2]

        residuals = {}
        for z in self._experimental_kratios.keys():
            current_wf = current_composition.get(z, 0.0)
            previous_wf = previous_composition.get(z, 0.0)

            residual = abs(current_wf - previous_wf)
            if residual > self._limit:
                residuals[z] = residual

        index = len(self._compositions) - 1
        logging.debug('Iteration %i - estimate: %s', index, current_composition)
        logging.debug('Iteration %i - residual: %s', index, residuals)

        return not residuals

class KRatioConvergor(_LimitConvergor):

    def has_converged(self):
        calculated_kratios = self._calculated_kratios[-1]

        residual = 0.0

        for z, experimental_kratio in self._experimental_kratios.iteritems():
            residual += (experimental_kratio[0] - calculated_kratios.get(z, 0.0)[0]) ** 2

        residual = math.sqrt(residual)

        index = len(self._compositions) - 1
        logging.debug('Iteration %i - residual: %s', index, residual)

        return residual < self._limit
