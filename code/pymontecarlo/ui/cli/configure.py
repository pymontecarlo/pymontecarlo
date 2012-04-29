#!/usr/bin/env python
"""
================================================================================
:mod:`configure` -- Script to configure settings
================================================================================

.. module:: configure
   :synopsis: Script to configure settings

.. inheritance-diagram:: pymontecarlo.ui.cli.configure

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
from pymontecarlo import load_settings, load_programs
from pymontecarlo.ui.cli.console import create_console
from pymontecarlo.util.config import ConfigParser

# Globals and constants variables.
from pymontecarlo.program.config import \
    TYPE_FILE, TYPE_DIR, TYPE_INT, TYPE_BOOL, TYPE_FLOAT, TYPE_TEXT

TYPE_LOOKUP = \
    {TYPE_FILE: 'prompt_file',
     TYPE_DIR: 'prompt_directory',
     TYPE_INT: 'prompt_int',
     TYPE_BOOL: 'prompt_bool',
     TYPE_FLOAT: 'prompt_float',
     TYPE_TEXT: 'prompt_text',
     }

def _find_programs():
    settings = load_settings(['/home/ppinard/documents/workspace/pydev/pymontecarlo/code/pymontecarlo/settings.cfg.example'])
    return load_programs(settings, validate=False)

def run(argv=None):
    # Initialize
    console = create_console()
    console.init()

    console.print_message("Configuration of pyMonteCarlo")
    console.print_line()

    # Find settings.cfg
    filepath = os.path.join(os.path.expanduser('~'), '.pymontecarlo', 'settings.cfg')
    if os.path.exists(filepath):
        console.print_message("A settings.cfg was found in '%s'" % filepath)

        answer = console.prompt_boolean("Do you want to overwrite these settings?", False)
        if not answer:
            console.close()

        settings = load_settings([filepath])
    else:
        console.print_message("No settings.cfg was found. This wizard will help you create one.")
        console.print_message("The settings.cfg will be saved in %s" % filepath)

        settings = ConfigParser() # Empty settings

    console.print_line()

    # Programs
    programs = []

    for program in _find_programs():
        answer = \
            console.prompt_boolean("Do you want to setup %s?" % program.name, True)
        if answer:
            params = program.configure_params
            for section_name, option_name, question, type in params:
                section = settings.add_section(section_name)

                try:
                    default = getattr(section, option_name)
                except AttributeError:
                    default = None

                method = TYPE_LOOKUP[type]
                value = getattr(console, method)(question, default)

                setattr(section, option_name, str(value))

            programs.append(program.alias)
        else:
            if program.alias in settings:
                delattr(settings, program.alias)

        console.print_line()

    # Save
    settings.add_section('pymontecarlo').programs = ','.join(programs)

    dirname = os.path.dirname(filepath)
    if not os.path.exists(dirname):
        os.mkdir(dirname)

    with open(filepath, 'w') as fileobj:
        settings.write(fileobj)
    console.print_success("Settings saved in %s" % filepath)

    # Finalize
    console.close()

if __name__ == '__main__':
    run()
