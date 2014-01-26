#!/usr/bin/env python
"""
================================================================================
:mod:`exporter` -- Exporter to PENSHOWER files
================================================================================

.. module:: exporter
   :synopsis: Exporter to PENSHOWER files

.. inheritance-diagram:: pymontecarlo.program.penshower.input.exporter

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import math
from operator import mul

# Third party modules.

# Local modules.
from pymontecarlo.settings import get_settings

from pymontecarlo.options.particle import ELECTRON, PHOTON, POSITRON
from pymontecarlo.options.limit import ShowersLimit
from pymontecarlo.options.detector import TrajectoryDetector

from pymontecarlo.program._penelope.exporter import \
    Exporter as _Exporter, Keyword, Comment

# Globals and constants variables.
MAX_PHOTON_DETECTORS = 25 # Set in penepma.f
MAX_PRZ = 20 # Set in penepma.f
MAX_PHOTON_DETECTOR_CHANNEL = 1000

_PARTICLES_REF = {ELECTRON: 1, PHOTON: 2, POSITRON: 3}

class Exporter(_Exporter):
    _KEYWORD_TITLE = Keyword("TITLE")

    _KEYWORD_SKPAR = Keyword("SKPAR", "Kind of primary particle")
    _KEYWORD_SENERG = Keyword("SENERG", "Energy of the electron beam, in eV")
    _KEYWORD_SPOSIT = Keyword("SPOSIT", "Coordinates of the electron source")
    _KEYWORD_SDIREC = Keyword("SDIREC", "Direction angles of the beam axis, in deg")
    _KEYWORD_SAPERT = Keyword("SAPERT", "Beam aperture, in deg")
    _KEYWORD_SDIAM = Keyword('SDIAM', "Beam diameter, in cm")

    _KEYWORD_MFNAME = Keyword("MFNAME", "Material file, up to 20 chars")
    _KEYWORD_MSIMPA = Keyword("MSIMPA", "EABS(1:3),C1,C2,WCC,WCR")

    _KEYWORD_GEOMFN = Keyword("GEOMFN", "Geometry definition file, 20 chars")
    _KEYWORD_DSMAX = Keyword("DSMAX", "IB, maximum step length (cm) in body IB")

    _KEYWORD_RSEED = Keyword("RSEED", "Seeds of the random - number generator")
    _KEYWORD_TRJSC = Keyword("TRJSC", "Track secondary electrons?")
    _KEYWORD_NTRJM = Keyword("NTRJM", "Number of trajectories in the shower")

    _COMMENT_SKIP = Comment('.')
    _COMMENT_ELECTROBEAM = Comment('>>>>>>>> Electron beam definition.')
    _COMMENT_MATERIALDATA = Comment(">>>>>>>> Material data and simulation parameters.")
    _COMMENT_GEOMETRY = Comment(">>>>>>>> Geometry of the sample.")
    _COMMENT_JOBPROP = Comment(">>>>>>>> Job properties.")

    _KEYWORD_END = Keyword("END")

    def __init__(self):
        """
        Creates a exporter to PENSHOWER.
        """
        _Exporter.__init__(self, get_settings().penshower.pendbase)

    def _create_input_file(self, options, outputdir, geoinfo, matinfos, *args):
        # Create lines
        lines = []
        args = (lines, options, geoinfo, matinfos) + args

        self._append_title(*args)
        self._append_electron_beam(*args)
        self._append_material_data(*args)
        self._append_geometry(*args)
        self._append_job_properties(*args)

        lines.append(self._KEYWORD_END())

        # Create .in file
        filepath = os.path.join(outputdir, options.name + '.in')
        with open(filepath, 'w') as fp:
            for line in lines:
                fp.write(line + os.linesep)

        return filepath

    def _append_title(self, lines, options, geoinfo, matinfos, *args):
        text = options.name
        line = self._KEYWORD_TITLE(text)
        lines.append(line)

        lines.append(self._COMMENT_SKIP())

    def _append_electron_beam(self, lines, options, geoinfo, matinfos, *args):
        lines.append(self._COMMENT_ELECTROBEAM())

        text = _PARTICLES_REF[options.beam.particle]
        line = self._KEYWORD_SKPAR(text)
        lines.append(line)

        text = options.beam.energy_eV
        line = self._KEYWORD_SENERG(text)
        lines.append(line)

        text = list(map(mul, [1e2] * 3, options.beam.origin_m)) # to cm
        line = self._KEYWORD_SPOSIT(text)
        lines.append(line)

        text = list(map(math.degrees, [options.beam.direction_polar_rad,
                                       options.beam.direction_azimuth_rad]))
        line = self._KEYWORD_SDIREC(text)
        lines.append(line)

        text = 0.0
        line = self._KEYWORD_SAPERT(text)
        lines.append(line)

        text = options.beam.diameter_m * 1e2 # to cm
        line = self._KEYWORD_SDIAM(text)
        lines.append(line)

        lines.append(self._COMMENT_SKIP())

    def _append_job_properties(self, lines, options, geoinfo, matinfos, *args):
        lines.append(self._COMMENT_JOBPROP())

        #NOTE: No random number. PENSHOWER will select them.

        det = list(options.detectors.iterclass(TrajectoryDetector))[0][1]
        text = '1' if det.secondary else '0'
        line = self._KEYWORD_TRJSC(text)
        lines.append(line)

        limit = list(options.limits.iterclass(ShowersLimit))[0]
        text = '%e' % limit.showers
        line = self._KEYWORD_NTRJM(text)
        lines.append(line)

        lines.append(self._COMMENT_SKIP())
