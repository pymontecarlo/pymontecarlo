#!/usr/bin/env python
"""
================================================================================
:mod:`detector` -- Special utility method for PENEPEMA
================================================================================

.. module:: detector
   :synopsis: Special utility method for PENEPEMA

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

# Globals and constants variables.

def index_delimited_detectors(detectors, places=6):
    """
    Organizes delimited detectors to group detectors with the same opening
    together and assigns an index to each unique opening.
    The method returns two a :class:`dict`:

      * one where an index (starting at 0) is assigned to each detector key;
          keys: detector keys, values: index
      * one where all detectors are listed for each index;
          keys: index, values: list of detector keys

    :arg detectors: :class:`dict` of delimited detectors.
        That is a :class:`dict` where the key is a string identifying the detector
        and the value are delimited detectors.
    :arg places: number of significant digits to consider two detector openings
        to be equivalent
    """
    # Group same detector openings together
    openings = {}
    for detector_key, detector in detectors.items():
        # Create a key for the detector opening by looking only at the
        # significant digits
        opening = tuple(detector.elevation_rad) + tuple(detector.azimuth_rad)
        opening_key = tuple(map(round, opening, [places] * 4))

        openings.setdefault(opening_key, []).append(detector_key)

    # Sort opening
    opening_keys = sorted(openings.keys(), \
                          key=lambda item: (item[0], item[1], item[2], item[3]))

    # Assign index
    d1 = {}
    d2 = {}
    for index, opening_key in enumerate(opening_keys):
        for detector_key in openings[opening_key]:
            d1[detector_key] = index

        d2[index] = openings[opening_key]

    return d1, d2

