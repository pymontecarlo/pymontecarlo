#!/usr/bin/env python
"""
================================================================================
:mod:`config_cli` -- Monaco Monte Carlo program CLI configuration
================================================================================

.. module:: config_cli
   :synopsis: Monaco Monte Carlo program CLI configuration

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

class _MonacoCLI(CLI):

    def configure(self, console, settings):
        section = settings.add_section('monaco')

        # basedir
        question = 'Full path to base directory'
        default = getattr(section, 'basedir', None)

        def validator(basedir):
            mccli32_exe = os.path.join(basedir, 'Mccli32.exe')
            if not os.path.isfile(mccli32_exe):
                raise ValueError("No Mccli32.exe in Monaco base directory")

        section.basedir = \
            console.prompt_directory(question, default, should_exist=True,
                                     validators=[validator])

cli = _MonacoCLI()
