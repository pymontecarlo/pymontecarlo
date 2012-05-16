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
from pymontecarlo import get_programs
from pymontecarlo.input.options import Options

from pymontecarlo.runner.runner import Runner
from pymontecarlo.runner.creator import Creator

from pymontecarlo.ui.cli.console import create_console, ProgressBar

# Globals and constants variables.


def create_parser(programs):
    description = "pyMonteCarlo Command Line Interface. Runs simulation(s) " + \
                  "with different Monte Carlo programs from the same interface." + \
                  "After the simulations, the results are automatically saved " + \
                  "in the output directory."
    epilog = "For more information, see http://pymontecarlo.sf.net"

    parser = OptionParser(usage="%prog [options] [OPTION_FILE...]",
                          description=description, epilog=epilog)

    # Base options
    parser.add_option("-o", '--outputdir', dest="outputdir", default=os.getcwd(), metavar="DIR",
                      help="Output directory where results from simulation(s) will be saved [default: current directory]")
    parser.add_option("-w", '--workdir', dest="workdir", default=None, metavar="DIR",
                      help="Work directory where temporary files from simulation(s) will be stored [default: temporary folder]")
    parser.add_option('-v', '--verbose', dest='verbose', default=False,
                      action='store_true', help='Debug mode')
    parser.add_option("-n", dest="nbprocesses", default=1, type="int",
                      help="Number of processes/threads to use (not applicable for all Monte Carlo programs) [default: %default]")
    parser.add_option('-c', '--create', dest='create', default=False,
                      action='store_true', help='Create mode where only simulation files are created but not run')
    parser.add_option('-s', '--skip', dest='skip', default=False,
                      action='store_true', help='Skip simulation if results already exist')

    # Program group
    group = OptionGroup(parser, "Monte Carlo programs",
                        "Note: Specify only one of these flags. Only supported programs are shown.")

    for alias in map(attrgetter('alias'), programs):
        group.add_option('--%s' % alias, dest=alias, action="store_true")

    parser.add_option_group(group)

    return parser

def load_options(filepaths, list_options=[]):
    for filepath in filepaths:
        if os.path.isdir(filepath):
            load_options(glob.glob(os.path.join(filepath, '*.xml')), list_options)
            list_options.sort()
            return

        list_options.append(Options.load(filepath, validate=False))

def run(argv=None):
    # Initialize
    console = create_console()
    console.init()

    programs = get_programs()

    parser = create_parser(programs)

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

    nbprocesses = values.nbprocesses
    if nbprocesses <= 0:
        parser.error("Number of processes must be greater than 0.")

    overwrite = not values.skip

    aliases = map(attrgetter('alias'), programs)
    selected_programs = [alias for alias in aliases if getattr(values, alias)]
    if not selected_programs:
        console.print_error("Please select one Monte Carlo program")
    if len(selected_programs) > 1:
        console.print_error("Please select only one Monte Carlo program")
    selected_program = selected_programs[0]

    if not args:
        console.print_error("Please specify at least one options file")

    list_options = []
    try:
        load_options(args, list_options)
    except Exception as ex:
        console.print_error(str(ex))

    # Setup
    workers = dict(zip(aliases, map(attrgetter('worker'), programs)))
    worker_class = workers[selected_program]

    if values.create:
        runner = Creator(worker_class, outputdir, overwrite, nbprocesses)
    else:
        runner = Runner(worker_class, outputdir, workdir, overwrite, nbprocesses)

    progressbar = ProgressBar(console, len(list_options))
    progressbar.start()

    for options in list_options:
        runner.put(options)

    runner.start()

    try:
        while runner.is_alive():
            counter, progress, status = runner.report()
            progressbar.update(counter, progress, status)
            time.sleep(1)
    except Exception as ex:
        console.print_error(str(ex))

    runner.close()
    progressbar.close()

    # Clean up
    console.close()

if __name__ == '__main__':
    run()
