#!/usr/bin/env python
"""
================================================================================
:mod:`layout` -- Layout utilities
================================================================================

.. module:: layout
   :synopsis: Layout utilities

.. inheritance-diagram:: pymontecarlo.ui.gui.util.layout

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.
from PySide.QtGui import QFormLayout

# Local modules.

# Globals and constants variables.

def merge_formlayout(layout1, layout2):
    """
    Merge *layout2* in *layout1*.
    """
    for row in range(layout2.rowCount()):
        label = layout2.itemAt(row, QFormLayout.ItemRole.LabelRole)
        field = layout2.itemAt(row, QFormLayout.ItemRole.FieldRole)
        span = layout2.itemAt(row, QFormLayout.ItemRole.SpanningRole)

        if label and field:
            layout1.addRow(label.widget(), field.widget())
        elif span:
            layout1.addRow(span.widget())

    return layout1
