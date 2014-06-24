#!/usr/bin/env python
"""
================================================================================
:mod:`main` -- Main for the command line user interface
================================================================================

.. module:: main
   :synopsis: Main for the command line user interface

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
import glob
import logging
from operator import attrgetter
from optparse import OptionParser, OptionGroup

# Third party modules.

# Local modules.
from pymontecarlo.settings import get_settings

from pymontecarlo.options.options import Options

from pymontecarlo.runner.local import LocalRunner #, LocalCreator

from pymontecarlo.ui.cli.console import Console, ProgressBar

# Globals and constants variables.


def _create_parser(programs):
    description = "pyMonteCarlo Command Line Interface. Runs simulation(s) " + \
                  "with different Monte Carlo programs from the same interface." + \
                  "After the simulations, the results are automatically saved " + \
                  "in the output directory."
    epilog = "For more information, see http://pymontecarlo.bitbucket.org"

    parser = OptionParser(usage="%prog [options] [OPTION_FILE...]",
                          description=description, epilog=epilog)

    # Base options
    parser.add_option("-o", '--outputdir', dest="outputdir", default=os.getcwd(), metavar="DIR",
                      help="Output directory where results from simulation(s) will be saved [default: current directory]")
    parser.add_option("-w", '--workdir', dest="workdir", default=None, metavar="DIR",
                      help="Work directory where temporary files from simulation(s) will be stored [default: temporary folder]")
    parser.add_option('-v', '--verbose', dest='verbose', default=False,
                      action='store_true', help='Debug mode')
    parser.add_option('-q', '--quiet', dest='quiet', default=False,
                      action='store_true', help='Quite mode (no progress bar is shown)')
    parser.add_option("-n", dest="nbprocesses", default=1, type="int",
                      help="Number of processes/threads to use (not applicable for all Monte Carlo programs) [default: %default]")
    parser.add_option('-s', '--skip', dest='skip', default=False,
                      action='store_true', help='Skip simulation if results already exist')

    # Program group
    group = OptionGroup(parser, "Monte Carlo programs",
                        "Note: Only supported programs are shown.")

    for alias in sorted(map(attrgetter('alias'), programs)):
        group.add_option('--%s' % alias, dest=alias, action="store_true")

    parser.add_option_group(group)

    return parser

def _load(filepaths, list_options=None):
    for filepath in filepaths:
        if os.path.isdir(filepath):
            _load(glob.glob(os.path.join(filepath, '*.xml')), list_options)
            list_options.sort()
            return

        list_options.append(Options.read(filepath))

def run(argv=None):
    # Initialize
    console = Console()
    console.init()

    programs = get_settings().get_programs()

    parser = _create_parser(programs)

    # Parse arguments
    (values, args) = parser.parse_args(argv)

    # Check inputs
    outputdir = values.outputdir
    if not os.path.exists(outputdir):
        console.print_error("The specified output directory (%s) does not exist" % outputdir)

    workdir = values.workdir
    if workdir is not None and not os.path.exists(workdir):
        console.print_error("The specified work directory (%s) does not exist" % workdir)

    if values.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    quiet = values.quiet

    nbprocesses = values.nbprocesses
    if nbprocesses <= 0:
        parser.error("Number of processes must be greater than 0.")

    overwrite = not values.skip

    aliases = dict(zip(map(attrgetter('alias'), programs), programs))
    selected_aliases = [alias for alias in aliases if getattr(values, alias)]
    if not selected_aliases:
        console.print_error("Please select one Monte Carlo program")
    selected_programs = list(map(aliases.get, selected_aliases))

    list_options = []
    try:
        _load(args, list_options)
    except Exception as ex:
        console.print_error(str(ex))

    if not list_options:
        console.print_error("Please specify at least one options file")

    # Setup
    runner = LocalRunner(outputdir, workdir, overwrite, nbprocesses)

    progressbar = ProgressBar(console)
    if not quiet: progressbar.start()

    # Start simulation
    with runner:
        for options in list_options:
            options.programs.update(selected_programs)
            runner.put(options)

        try:
            while runner.is_alive():
                if not quiet: progressbar.update(runner.progress, runner.status)
                time.sleep(1)

        except Exception as ex:
            console.print_exception(ex)

    if not quiet: progressbar.close()

    # Clean up
    console.close()

if __name__ == '__main__':
    run()
