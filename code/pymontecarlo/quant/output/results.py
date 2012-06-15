#!/usr/bin/env python
"""
================================================================================
:mod:`results` -- Results from quantification
================================================================================

.. module:: results
   :synopsis: Results from quantification

.. inheritance-diagram:: pymontecarlo.qunat.output.results

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import csv
from zipfile import ZipFile
from StringIO import StringIO

# Third party modules.

# Local modules.
from pymontecarlo.util.config import ConfigParser

# Globals and constants variables.
from zipfile import ZIP_DEFLATED

VERSION = 1

class _CompositionResult(object):

    def __init__(self, compositions):
        """
        Result of the quantification containing the composition for each 
        iteration.
        
        :arg compositions: :class:`list` of composition ordered from the first
            to the last iteration
        :type compositions: :class:`list`
        """
        self._compositions = list(compositions) # copy

    def __len__(self):
        return len(self._compositions)

    def __iter__(self):
        return iter(self._compositions)

    def __getitem__(self, index):
        return self._compositions[index]

class Results(object):

    def __init__(self, compositions, elapsed_time_s, max_iterations,
                 convergence_limit, iterator):
        """
        Results from a quantification.
        
        :arg compositions: :class:`list` of composition ordered from the first
            to the last iteration
        :type compositions: :class:`list`
        
        :arg elapsed_time_s: total time of the quantification
        :type elapsed_time_s: :class:`float`
        
        :arg max_iterations: maximum number of iterations used
        :type max_iterations: :class:`int`
        
        :arg convergence_limit: convergence limit used
        :type convergence_limit: :class:`float`
        
        :arg iterator: name of the iterator used
        :type iterator: :class:`str`
        """
        if elapsed_time_s < 0:
            raise ValueError, 'Elapsed time cannot be less than 0'

        self._compositions = _CompositionResult(compositions)
        self._elapsed_time_s = elapsed_time_s
        self._max_iterations = max_iterations
        self._convergence_limit = convergence_limit
        self._iterator = iterator

    @classmethod
    def load(cls, source):
        """
        Loads results from a results ZIP.
        
        :arg source: filepath or file-object
        
        :return: results container
        """
        zipfile = ZipFile(source, 'r')

        # Check version
        if zipfile.comment != 'version=%s' % VERSION:
            raise IOError, "Incorrect version of results. Only version %s is accepted" % \
                    VERSION

        # Read compositions
        reader = csv.reader(zipfile.open('compositions.csv', 'r'))

        header = reader.next()
        zs = map(int, header[1:])

        compositions = []
        for row in reader:
            wfs = map(float, row[1:])
            composition = dict(zip(zs, wfs))
            compositions.append(composition)

        # Read stats
        config = ConfigParser()
        config.read(zipfile.open('stats.cfg', 'r'))

        section = config.stats
        elapsed_time_s = float(section.elapsed_time_s)
        iterations = int(section.iterations)
        convergence_limit = float(section.convergence_limit)
        max_iterations = int(section.max_iterations)
        iterator = section.iterator

        assert iterations == len(compositions)

        zipfile.close()

        return cls(compositions, elapsed_time_s, max_iterations,
                   convergence_limit, iterator)

    def save(self, source):
        """
        Saves results in a results ZIP.
        
        :arg source: filepath or file-object
        """
        zipfile = ZipFile(source, 'w', compression=ZIP_DEFLATED)
        zipfile.comment = 'version=%s' % VERSION

        # Save compositions
        fp = StringIO()
        writer = csv.writer(fp)

        zs = self._compositions[0].keys()
        writer.writerow(['iteration'] + zs)

        for i, composition in enumerate(self._compositions):
            writer.writerow([i + 1] + [composition[z] for z in zs])

        zipfile.writestr('compositions.csv', fp.getvalue())

        # Save stats
        config = ConfigParser()
        section = config.add_section('stats')

        section.elapsed_time_s = self.elapsed_time_s
        section.iterations = self.iterations
        section.convergence_limit = self.convergence_limit
        section.max_iterations = self.max_iterations
        section.iterator = self.iterator

        fp = StringIO()
        config.write(fp)
        zipfile.writestr('stats.cfg', fp.getvalue())

        zipfile.close()

    @property
    def compositions(self):
        """
        Composition of each iteration.
        
        To get the final composition,::
        
            >>> results.compositions[-1]
            
        """
        return self._compositions

    @property
    def elapsed_time_s(self):
        """
        Time for the quantification (in seconds).
        """
        return self._elapsed_time_s

    @property
    def iterations(self):
        """
        Number of iterations
        """
        return len(self._compositions)

    @property
    def convergence_limit(self):
        """
        Convergence limit used.
        """
        return self._convergence_limit

    @property
    def max_iterations(self):
        """
        Maximum number of iterations used.
        """
        return self._max_iterations

    @property
    def iterator(self):
        """
        Name of the iterator used.
        """
        return self._iterator
