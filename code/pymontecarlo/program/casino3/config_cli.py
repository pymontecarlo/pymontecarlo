#!/usr/bin/env python
"""
================================================================================
:mod:`config_cli` -- Casino 3 Monte Carlo program CLI configuration
================================================================================

.. module:: config_cli
   :synopsis: Casino 3 Monte Carlo program CLI configuration

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
from pymontecarlo.program.config_cli import CLI

# Globals and constants variables.

class _Casino3CLI(CLI):

    def configure(self, console, settings):
        section = settings.add_section('casino3')

        # exe
        question = 'Full path to console_casino3_script.exe'
        default = getattr(section, 'exe', None)
        section.exe = console.prompt_file(question, default, should_exist=True)

cli = _Casino3CLI()
