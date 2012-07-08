#!/usr/bin/env python
"""
================================================================================
:mod:`iterator` -- Quantitative iterator algorithm
================================================================================

.. module:: iterator
   :synopsis: Quantitative iterator algorithm

.. inheritance-diagram:: pymontecarlo.quant.iterator

.. note::

   Algorithm implemented with the help of the IterationAlgorithm class of 
   DTSA-II.

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.
import numpy as np

# Local modules.
import pymontecarlo.util.element_properties as ep

# Globals and constants variables.

class _Iterator(object):
    def __init__(self, experimental_kratios, composition):
        """
        Creates a new quantitative iterator.
        
        :arg experimental_kratios: experimental k-ratios for each element given 
            as a :class:`dict` where the keys are atomic numbers and the values
            are tuples of the experimental k-ratios and their uncertainties.
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

        self.reset()

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
        Returns a new composition from the specified calculated k-ratios
        
        :arg calculated_kratios: theoretical k-ratios for each element given as a 
            :class:`dict` where the keys are atomic numbers and the values
            are tuples of the theoretical k-ratios and their uncertainties.
        :type calculated_kratios: :class:`dict`
        
        :return: next composition
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
        :type z: :class:`int`
        
        :arg experimental_kratio: tuple of experimental k-ratio of this element
            and its uncertainty
        :type experimental_kratio: :class:`tuple`
            
        :arg calculated_kratio: tuple of the calculated k-ratio of this element
            and its uncertainty
        :type calculated_kratio: :class:`tuple`
        
        :arg wfs: list of weight fractions of this element from the previous
            iterations. Calling ``wfs[-1]`` will always return the last
            calculated weight fraction.
        :type wfs: :class:`list`
        """
        raise NotImplementedError

class SimpleIterator(_Iterator):
    """
    Using method reported in Scott, Love and Reed (1992).
    """

    def _iterate(self, z, experimental_kratio, calculated_kratio, wfs):
        wf = wfs[-1] # Take weight fraction from last iteration

        try:
            correction = calculated_kratio[0] / wf
            return experimental_kratio[0] / correction
        except ZeroDivisionError:
            return 0.0

class Heinrich1972Iterator(_Iterator):
    """
    Using method of Ziebold and Ogilvie (1964) as reported in Scott, Love and 
    Reed (1992).
    """

    def _iterate(self, z, experimental_kratio, calculated_kratio, wfs):
        wf = wfs[-1] # Take weight fraction from last iteration

        try:
            alpha = (wf * (1 - calculated_kratio[0])) / \
                        (calculated_kratio[0] * (1 - wf))
            return (alpha * experimental_kratio[0]) / \
                        (1.0 - experimental_kratio[0] * (1.0 - alpha))
        except ZeroDivisionError:
            return 0.0

#        Using method reported in Heinrich (1972).
#    
#        Reference: Heinrich, K. F. J. Errors in theoretical correction systems
#            in quantitative electron probe microanalysis.
#            Synopsis Analytical Chemistry, 1972, 44, 350-354
#
#        nominator = experimental_kratio * wf * (1.0 - calculated_kratio)
#        term1 = experimental_kratio * (wf - calculated_kratio)
#        term2 = calculated_kratio * (1.0 - wf)
#        denominator = term1 + term2
#
#        try:
#            return nominator / denominator
#        except ZeroDivisionError:
#            return 0.0

class Pouchou1991Iterator(Heinrich1972Iterator):
    """
    Using method reported in Pouchou (1991).
    
    Reference: Pouchou, J.-L. and Pichoir, F. (1991). Quantitative analysis of
        homogeneous or stratified microvolumes applying the model "PAP". In 
        Electron Probe Quantitation, K.F.J. Heinrich and D.E. Newbury, 
        Plenum Press, New York, 400 p.
    """

    def _iterate(self, z, experimental_kratio, calculated_kratio, wfs):
        wf = wfs[-1] # Take weight fraction from last iteration

        if calculated_kratio[0] / wf <= 1: # Hyperbolic
            return Heinrich1972Iterator._iterate(self, z, experimental_kratio,
                                          calculated_kratio, wfs)
        else: # Parabolic
            # From DTSA 2
            alpha = (calculated_kratio[0] - wf ** 2) / (wf - wf ** 2)
            roots = np.roots([calculated_kratio[0], alpha, (1 - alpha)])
            return max(roots)

class Wegstein1958Iterator(SimpleIterator):
    """
    Using method of Wegstein (1958) as reported in Scott, Love and Reed (1992).
    """

    def reset(self):
        SimpleIterator.reset(self)
        self._calculated_kratios = []

    def next(self, calculated_kratios):
        composition = SimpleIterator.next(self, calculated_kratios)
        self._calculated_kratios.append(calculated_kratios)
        return composition

    def _iterate(self, z, experimental_kratio, calculated_kratio, wfs):
        if len(wfs) < 2: # Use simple iterator
            return SimpleIterator._iterate(self, z, experimental_kratio,
                                           calculated_kratio, wfs)
        else: # Wegstein
            wf1 = wfs[-1]
            wf2 = wfs[-2]
            calculated_kratio1 = calculated_kratio[0]
            calculated_kratio2 = self._calculated_kratios[-1][z][0]

            fa1 = wf1 / calculated_kratio1
            fa2 = wf2 / calculated_kratio2

            derivative = (fa1 - fa2) / (wf1 - wf2)

            return wf1 + (experimental_kratio[0] * fa1 - wf1) / \
                            (1 - experimental_kratio[0] * derivative)
