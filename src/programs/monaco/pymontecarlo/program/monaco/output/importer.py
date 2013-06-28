#!/usr/bin/env python
"""
================================================================================
:mod:`importer` -- Monaco results importer
================================================================================

.. module:: importer
   :synopsis: Monaco results importer

.. inheritance-diagram:: pymontecarlo.program.monaco.output.importer

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import csv

# Third party modules.
import numpy as np

from pyxray.transition import from_string

# Local modules.
from pymontecarlo.output.importer import Importer as _Importer, ImporterException

from pymontecarlo.input.detector import \
    PhotonIntensityDetector, PhotonDepthDetector

from pymontecarlo.output.result import \
    (PhotonIntensityResult, create_intensity_dict,
     PhotonDepthResult, create_photondist_dict)

# Globals and constants variables.

class Importer(_Importer):

    def __init__(self):
        _Importer.__init__(self)

        self._detector_importers[PhotonIntensityDetector] = \
            self._detector_photon_intensity
        self._detector_importers[PhotonDepthDetector] = self._detector_photondepth

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
        intensities_filepath = os.path.join(jobdir, 'intensities_%s.csv' % name)
        if not os.path.exists(intensities_filepath):
            raise ImporterException, \
                'Result file "intensites_%s.csv" not found in job directory (%s)' % \
                    (name, jobdir)

        intensities = {}

        with open(intensities_filepath, 'r') as fp:
            reader = csv.DictReader(fp)
            row = list(reader)[0]

        for transition, intensity in row.iteritems():
            transition = from_string(transition.strip())
            enf = (float(intensity.strip()), 0.0)

            intensities.update(create_intensity_dict(transition, 
                                                     enf=enf, et=enf))
            
        return PhotonIntensityResult(intensities)

    def _detector_photondepth(self, options, name, detector, jobdir):
        prz_filepath = os.path.join(jobdir, 'phi_%s.csv' % name)
        if not os.path.exists(prz_filepath):
            raise ImporterException, \
                'Result file "phi_%s.csv" not found in job directory (%s)' % \
                    (name, jobdir)

        with open(prz_filepath, 'r') as fp:
            reader = csv.reader(fp)
            header = reader.next()

            data = {}
            for row in reader:
                for i, val in enumerate(row):
                    data.setdefault(header[i], []).append(float(val))

        rzs = np.array(data.pop('rho z'))
        
        distributions = {}
        for transition, values in data.iteritems():
            transition = from_string(transition.strip())

            enf = np.array([rzs, values]).transpose()

            distributions.update(create_photondist_dict(transition,
                                                        enf=enf, et=enf))

        return PhotonDepthResult(distributions)
