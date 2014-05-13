#!/usr/bin/env python
"""
================================================================================
:mod:`updater` -- Script to update options or results file to current version
================================================================================

.. module:: updater
   :synopsis: Script to update options or results file to current version

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os.path
import logging
from optparse import OptionParser

# Third party modules.

# Local modules.
from pymontecarlo.settings import get_settings
from pymontecarlo.ui.cli.console import Console
from pymontecarlo.options.updater import Updater as OptionsUpdater
from pymontecarlo.results.updater import Updater as ResultsUpdater

# Globals and constants variables.

def run(argv=None):
    # Initialise programs
    get_settings().get_programs()

    # Initialise console
    console = Console()
    console.init()

    # Create parser
    usage = "%prog [options] [OPTION_FILE.xml or RESULTS_FILE.zip or RESULTS_FILE.h5 ...]"
    description = "pyMonteCarlo update tool. This script updates old version " + \
                  "of options or results file to the newer one."
    epilog = "For more information, see http://pymontecarlo.bitbucket.org"

    parser = OptionParser(usage=usage, description=description, epilog=epilog)

    parser.add_option('-v', '--verbose', dest='verbose', default=False,
                      action='store_true', help='Debug mode')

    # Parse arguments
    (values, args) = parser.parse_args(argv)

    if values.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not args:
        console.print_error('Please specify at least one file')

    for filepath in args:
        if not os.path.exists(filepath):
            console.print_error('File %s does not exists' % filepath)

        ext = os.path.splitext(filepath)[1]

        if ext == '.xml':
            console.print_info("Updating options %s" % filepath)
            filepath = OptionsUpdater().update(filepath)
            console.print_success("Successfully updated %s" % filepath)
        elif ext == '.zip' or ext == '.h5':
            console.print_info("Updating results %s" % filepath)
            filepath = ResultsUpdater().update(filepath)
            console.print_success("Successfully results %s" % filepath)
        else:
            console.print_error('Unknown extension %s' % ext)

    console.close()

if __name__ == '__main__':
    run()
