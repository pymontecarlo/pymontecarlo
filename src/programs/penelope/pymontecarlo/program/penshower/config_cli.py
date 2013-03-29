#!/usr/bin/env python
"""
================================================================================
:mod:`config_cli` -- PENSHOWER Monte Carlo program CLI configuration
================================================================================

.. module:: config_cli
   :synopsis: PENSHOWER Monte Carlo program CLI configuration

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os

# Third party modules.

# Local modules.
from pymontecarlo.program.config_cli import CLI

# Globals and constants variables.

class _PenshowerCLI(CLI):

    def configure(self, console, settings):
        section = settings.add_section('penshower')

        # Pendbase
        question = 'Path to pendbase directory'
        default = getattr(section, 'pendbase', None)
        section.pendbase = \
            console.prompt_directory(question, default, should_exist=True)

        # exe
        question = 'Path to PENSHOWER executable'
        default = getattr(section, 'exe', None)
        section.exe = console.prompt_file(question, default,
                                          should_exist=True, mode=os.X_OK)

cli = _PenshowerCLI()
