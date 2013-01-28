#!/usr/bin/env python
"""
================================================================================
:mod:`config_setup` -- Pouchou setup configuration
================================================================================

.. module:: config_setup
   :synopsis: Pouchou setup configuration

.. inheritance-diagram:: pymontecarlo.program._pouchou.config_setup

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os

# Third party modules.

# Local modules.
from pymontecarlo.program.config_setup import Setup

import DatabasesTools
import DrixUtilities
import MassAbsorptionCoefficientTools
import NumericalMethodsTools
import PouchouPichoirModels
import SpecimenTools

# Globals and constants variables.

class _PouchouSetup(Setup):

    def __init__(self, packages=None, py_modules=None, package_dir=None,
                 package_data=None, ext_modules=None, cmdclass=None):
        if packages is None: packages = []
        packages += ['pymontecarlo.program._pouchou',
                     'pymontecarlo.program._pouchou.input',
                     'pymontecarlo.program._pouchou.runner',
                     'DatabasesTools.DTSA',
                     'PouchouPichoirModels.models',
                     'MassAbsorptionCoefficientTools',
                     'DatabasesTools.Mac',
                     'DatabasesTools.Mac.Henke',
                     'DatabasesTools.Brunetti2004',
                     'DatabasesTools.deboer1989']

        if py_modules is None: py_modules = []
        py_modules += ['DatabasesTools.XRayTransitionName',
                       'DatabasesTools.XRayDataWinxray',
                       'DatabasesTools.ElementProperties',
                       'DrixUtilities.XMLTools',
                       'PouchouPichoirModels.__init__',
                       'SpecimenTools.Element',
                       'NumericalMethodsTools.__init__',
                       'NumericalMethodsTools.Interpolation.Interpolation1D']

        if package_dir is None: package_dir = {}
        package_dir.update({'DatabasesTools': os.path.dirname(DatabasesTools.__file__),
                            'DrixUtilities': os.path.dirname(DrixUtilities.__file__),
                            'MassAbsorptionCoefficientTools': os.path.dirname(MassAbsorptionCoefficientTools.__file__),
                            'NumericalMethodsTools': os.path.dirname(NumericalMethodsTools.__file__),
                            'PouchouPichoirModels': os.path.dirname(PouchouPichoirModels.__file__),
                            'SpecimenTools': os.path.dirname(SpecimenTools.__file__)})

        if package_data is None: package_data = {}
        package_data.update({'pymontecarlo.program._pouchou': ['data/*']})

        Setup.__init__(self, packages, py_modules, package_dir, package_data,
                       ext_modules, cmdclass)
