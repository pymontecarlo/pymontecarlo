#!/usr/bin/env python
"""
================================================================================
:mod:`main` -- Main for the command line user interface
================================================================================

.. module:: main
   :synopsis: Main for the command line user interface

.. inheritance-diagram:: main

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import time
import platform
#import multiprocessing
import logging
from optparse import OptionParser, OptionGroup

# Third party modules.

# Local modules.
from pymontecarlo.input.base.options import Options

import pymontecarlo.runner.casino2.runner #@UnusedImport
import pymontecarlo.runner.nistmonte.runner #@UnusedImport
import pymontecarlo.runner.winxray.runner #@UnusedImport

from pymontecarlo.runner.base.manager import RunnerManager

from pymontecarlo.ui.cli.console import create_console, ProgressBar

# Globals and constants variables.


def create_parser(flags):
    description = "pyMonteCarlo Command Line Interface. Runs simulation(s) " + \
                  "with different Monte Carlo programs from the same interface." + \
                  "After the simulations, the results are automatically saved " + \
                  "in the output directory."
    epilog = "For more information, see http://pymontecarlo.sf.net"

    parser = OptionParser(usage="%prog [options] [OPTION_FILE...]",
                          description=description, epilog=epilog)

    # Base options
    parser.add_option("-o", '--outputdir', dest="outputdir", default=os.getcwd(), metavar="DIR",
                      help="Output directory where the results from the simulation(s) will be saved [default: current directory]")
    parser.add_option('-v', '--verbose', dest='verbose', default=False,
                      action='store_true', help='Debug mode')
#    parser.add_option("-n", dest="nprocessors", default=1, type="int",
#                      help="Number of processors to use (not applicable for all Monte Carlo programs) [default: %default]")

    # Program group
    group = OptionGroup(parser, "Monte Carlo programs",
                        "Note: Specify only one of these flags. Only supported programs are shown.")

    for flag in flags:
        group.add_option('--%s' % flag, dest=flag, action="store_true")

    parser.add_option_group(group)

    return parser

def run(argv=None):
    # Initialize
    console = create_console()
    console.init()

    flags = RunnerManager.get_runners(platform.system())
    parser = create_parser(flags)

    # Parse arguments
    (values, args) = parser.parse_args(argv)

    # Check inputs
    outputdir = values.outputdir
    if not os.path.exists(outputdir):
        console.error("The specified output directory (%s) does not exist" % outputdir)

    if values.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

#    nprocessors = values.nprocessors
#    if nprocessors <= 0:
#        parser.error("Number of processors must be greater than 0.")
#    if nprocessors > multiprocessing.cpu_count():
#        parser.error("Number of processors is greater than the number of available processors (%i)" % \
#                     multiprocessing.cpu_count())

    selected_flags = [flag for flag in flags if getattr(values, flag)]
    if not selected_flags:
        console.error("Please select one Monte Carlo program")
    if len(selected_flags) > 1:
        console.error("Please select only one Monte Carlo program")
    selected_flag = selected_flags[0]

    if not args:
        console.error("Please specify at least one options file")

    options = []
    for arg in args:
        try:
            options.append(Options.load(arg, validate=False))
        except Exception as ex:
            console.error("Error while loading %s: %s" % (arg, str(ex)))

    # Setup runner
    runner = RunnerManager.get_runner(selected_flag)(options, outputdir)
    progressbar = ProgressBar(console, len(options))

    # Run
    progressbar.start()
    runner.start()

    while runner.is_alive():
        counter, progress, status = runner.report()
        progressbar.update(counter, progress, status)
        time.sleep(1)

    runner.join()
    progressbar.close()

    # Export results
    results = runner.get_results()
    for result in results:
        name = result.options.name
        filepath = os.path.join(outputdir, name + ".zip")
        result.save(filepath)

        console.info("Saved results of options '%s' in '%s'" % (name, filepath))

    # Clean up
    console.close()

if __name__ == '__main__':
    run()
