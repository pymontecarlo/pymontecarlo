#!/usr/bin/env python
"""
================================================================================
:mod:`importer` -- Monaco results importer
================================================================================

.. module:: importer
   :synopsis: Monaco results importer

.. inheritance-diagram:: pymontecarlo.program.monaco.io.importer

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os

# Third party modules.

# Local modules.
from pymontecarlo.io.importer import Importer as _Importer, ImporterException

from pymontecarlo.input.detector import PhotonIntensityDetector

from pymontecarlo.output.result import \
    PhotonIntensityResult, create_intensity_dict

import pymontecarlo.util.element_properties as ep
from pymontecarlo.util.transition import Ka, La, Ma

# Globals and constants variables.

class Importer(_Importer):

    def __init__(self):
        _Importer.__init__(self)

        self._detector_importers[PhotonIntensityDetector] = \
            self._detector_photon_intensity

    def import_from_dir(self, options, jobdir):
        """
        Imports Monaco results from a job directory.
        
        :arg options: options of the simulation
        :type options: :class:`Options <pymontecarlo.input.base.options.Options>`
        
        :arg path: location of the results directory
        """
        if not os.path.isdir(jobdir):
            raise ValueError, "Specified path (%s) is not a directory" % jobdir
        return self._import_results(options, jobdir)

    def _detector_photon_intensity(self, options, name, detector, jobdir):
        intensities_filepath = os.path.join(jobdir, 'intensities.txt')
        if not os.path.exists(intensities_filepath):
            raise ImporterException, \
                'Result file "intensites.txt" not found in job directory (%s)' % jobdir

        intensities = {}

        with open(intensities_filepath, 'r') as fp:
            for line in fp:
                line = line.strip()
                if not line: break

                transitionstr, intensity = line.split(',')
                symbol, line = transitionstr.split()
                z = ep.atomic_number(symbol)
                transition = {'K': Ka, 'L': La, 'M': Ma}[line[0]](z)

                enf = (float(intensity), 0.0)
                intensities.update(create_intensity_dict(transition,
                                                         enf=enf, et=enf))

        return PhotonIntensityResult(intensities)
