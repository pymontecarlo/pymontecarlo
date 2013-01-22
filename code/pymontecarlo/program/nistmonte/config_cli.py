#!/usr/bin/env python
"""
================================================================================
:mod:`config_cli` -- NISTMonte Monte Carlo program CLI configuration
================================================================================

.. module:: config_cli
   :synopsis: NISTMonte Monte Carlo program CLI configuration

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

class _NISTMonteCLI(CLI):

    def configure(self, console, settings):
        section = settings.add_section('nistmonte')

        # java
        question = 'Path to Java executable'
        default = getattr(section, 'java', None)
        section.java = \
            console.prompt_file(question, default, should_exist=True)

        # jar
        question = 'Path to pymontecarlo-nistmonte jar'
        default = getattr(section, 'jar', None)
        section.jar = console.prompt_file(question, default, should_exist=True)

cli = _NISTMonteCLI()
