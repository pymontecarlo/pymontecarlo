#!/usr/bin/env python
"""
================================================================================
:mod:`registry` -- Access entry points
================================================================================

.. module:: registry
   :synopsis: Access entry points

.. inheritance-diagram:: pymontecarlo.ui.gui.util.registry

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.
from pkg_resources import iter_entry_points

# Local modules.

# Globals and constants variables.

def get_widget_class(group, clasz):
    name = clasz.__name__
    entry_points = list(iter_entry_points(group, name))
    if not entry_points:
        raise ValueError("No widget found for %s" % name)
    if len(entry_points) > 1:
        raise ValueError("%i widgets found for %s" % (len(entry_points), name))

    entry_point = entry_points[0]
    return entry_point.load()