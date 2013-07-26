#!/usr/bin/env python
"""
================================================================================
:mod:`expander` -- Expand a options to several options with single value
================================================================================

.. module:: expander
   :synopsis: Expand a options to several options with single value

.. inheritance-diagram:: expander

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.input.parameter import Expander as _Expander
from pymontecarlo.input.options import Options

# Globals and constants variables.

class Expander(_Expander):
    """
    Special expander for the options to automatically generate a meaningful
    name for each options based on the varied parameter.
    """

    def expand(self, options):
        if not isinstance(options, Options):
            raise ValueError, "Argument must be an Options"
        return _Expander.expand(self, options)

    def _create_objects(self, baseobj, combinations, parameter_objs, parameters):
        opss = _Expander._create_objects(self, baseobj, combinations,
                                         parameter_objs, parameters)

        for options, combination in zip(opss, combinations):
            parts = [options.name]

            for parameter, value in zip(parameters, combination):
                parts.append('%s=%s' % (parameter.name, value))

            options.name = '+'.join(parts)

        return opss
