#!/usr/bin/env python
"""
================================================================================
:mod:`iterator` -- Quantitative iterator algorithm
================================================================================

.. module:: iterator
   :synopsis: Quantitative iterator algorithm

.. inheritance-diagram:: pymontecarlo.quant.iterator

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.

# Local modules.
import pymontecarlo.util.element_properties as ep

# Globals and constants variables.

class _Iterator(object):
    def __init__(self, experimental_kratios, composition):
        """
        Creates a new quantitative iterator.
        
        :arg experimental_kratios: experimental k-ratios for each element given 
            as a :class:`dict` where the keys are atomic numbers and the values
            are experimental k-ratios.
        :type experimental_kratios: :class:`dict`
        
        :arg composition: initial composition for each element give as a 
            :class:`dict` where they keys are atomic numbers and the values
            are weight fractions.
        :type composition: :class:`dict`
        """
        # Verify that each element has an experimental k-ratio
        kratios_zs = set(experimental_kratios.keys())
        composition_zs = set(composition.keys())
        missing_zs = kratios_zs - composition_zs
        if missing_zs:
            symbols = map(ep.symbol, missing_zs)
            raise ValueError, 'No k-ratio found for these elements: %s' % \
                    ', '.join(symbols)

        self._experimental_kratios = dict(experimental_kratios) # copy
        self._initial_composition = dict(composition) # copy

        self._iterations = [composition]

    def __len__(self):
        """
        Number of iterations.
        """
        return len(self._iterations) - 1

    def __getitem__(self, index):
        """
        Returns copy of the iterated composition with the specified index.
        """
        return dict(self._iterations[index])

    def __iter__(self):
        return iter(self._iterations[1:])

    @property
    def experimental_kratios(self):
        """
        Experimental k-ratios
        """
        return self._experimental_kratios

    def reset(self):
        """
        Resets the iterations.
        """
        self._iterations = [self._initial_composition]

    def next(self, calculated_kratios):
        """
        
        :arg kratios: theoretical kratios for each element given as a 
            :class:`dict` where the keys are atomic numbers and the values
            are experimental k-ratios.
        :type kratios: :class:`dict`
        
        :return: composition
        """
        composition = {}

        for z, calculated_kratio in calculated_kratios.iteritems():
            try:
                experimental_kratio = self._experimental_kratios[z]
            except KeyError:
                continue

            wfs = [iteration.get(z, 0.0) for iteration in self._iterations]

            wf = self._iterate(z, experimental_kratio,
                               calculated_kratio, wfs)

            if wf > 0.0:
                composition[z] = wf

        self._iterations.append(composition)
        return composition

    def _iterate(self, z, experimental_kratio, calculated_kratio, wfs):
        """
        Calculates the next weight fraction of an element.
        
        :arg z: atomic number of element
        :arg experimental_kratio: experimental k-ratio of this element
        :arg experimental_kratio: calculated k-ratio of this element
        :arg wfs: list of weight fractions of this element from the previous
            iterations. Calling ``wfs[-1]`` will always return the last
            calculated weight fraction.
        """
        raise NotImplementedError

class Heinrich1972Iterator(_Iterator):
    """
    Using method reported in Heinrich (1972).
    
    Reference: Heinrich, K. F. J. Errors in theoretical correction systems
        in quantitative electron probe microanalysis.
        Synopsis Analytical Chemistry, 1972, 44, 350-354
    """

    def _iterate(self, z, experimental_kratio, calculated_kratio, wfs):
        wf = wfs[-1] # Take weight fraction from last iteration

        nominator = experimental_kratio * wf * (1.0 - calculated_kratio)
        term1 = experimental_kratio * (wf - calculated_kratio)
        term2 = calculated_kratio * (1.0 - wf)
        denominator = term1 + term2

        try:
            return nominator / denominator
        except ZeroDivisionError:
            return 0.0
