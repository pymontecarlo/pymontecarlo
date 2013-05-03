#!/usr/bin/env python
"""
================================================================================
:mod:`configure` -- Script to configure settings
================================================================================

.. module:: configure
   :synopsis: Script to configure settings

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
from pymontecarlo.settings import get_settings
from pymontecarlo.ui.cli.console import Console

# Globals and constants variables.

def run(argv=None):
    # Initialize
    console = Console()
    console.init()

    console.print_message("Configuration of pyMonteCarlo")
    console.print_line()

    # Find settings.cfg
    settings = get_settings()

    # Programs
    programs = []

    for program_alias in settings.get_available_program_aliases():
        default = program_alias in settings.get_program_aliases()
        answer = \
            console.prompt_boolean("Do you want to setup %s?" % program_alias, default)
        if answer:
            cli = settings.get_program_cli(program_alias)
            try:
                pass
            except Exception as ex:
                console.print_exception(ex)
                return

            cli.configure(console, settings)

            programs.append(program_alias)
        else:
            if program_alias in settings:
                delattr(settings, program_alias)

        console.print_line()

    settings.pymontecarlo.programs = ','.join(programs)

    # Save
    settings.write()
    console.print_success("Settings saved")

    # Finalize
    console.close()

if __name__ == '__main__':
    run()
