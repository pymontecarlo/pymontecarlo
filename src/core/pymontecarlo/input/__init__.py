#!/usr/bin/env python
"""
================================================================================
:mod:`input` -- Input modules to generate Monte Carlo simulations
================================================================================

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
from pymontecarlo.util.xmlmapper import XMLMapper, Attribute, PythonType
from pymontecarlo.util.mathutil import vector2d, vector3d

#from pymontecarlo.input.beam import *
#from pymontecarlo.input.body import *
#from pymontecarlo.input.collision import *
#from pymontecarlo.input.detector import *
#from pymontecarlo.input.geometry import *
#from pymontecarlo.input.limit import *
#from pymontecarlo.input.material import *
#from pymontecarlo.input.model import *
#from pymontecarlo.input.options import *
#from pymontecarlo.input.particle import *

# Globals and constants variables.

mapper = XMLMapper()
mapper.register_namespace('mc', 'http://pymontecarlo.sf.net')

# Register classes in pymontecarlo.util
mapper.register(vector3d, "vector3d",
                Attribute('x', PythonType(float)),
                Attribute('y', PythonType(float)),
                Attribute('z', PythonType(float)))

mapper.register(vector2d, "vector2d",
                Attribute('x', PythonType(float)),
                Attribute('y', PythonType(float)))


#

