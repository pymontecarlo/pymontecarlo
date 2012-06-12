#!/usr/bin/env python
"""
================================================================================
:mod:`quant` -- Quantification of experimental results
================================================================================

.. module:: quant
   :synopsis: Quantification of experimental results

.. inheritance-diagram:: pymontecarlo.ui.cli.quant

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
import logging
import csv
from operator import attrgetter
from optparse import OptionParser, OptionGroup

# Third party modules.

# Local modules.
from pymontecarlo import get_programs

from pymontecarlo.analysis.measurement import Measurement
from pymontecarlo.analysis.quant import Quantification
from pymontecarlo.analysis.iterator import Heinrich1972Iterator, Pouchou1991Iterator

from pymontecarlo.runner.runner import Runner

from pymontecarlo.ui.cli.console import create_console, ProgressBar

import pymontecarlo.util.element_properties as ep

# Globals and constants variables.

def create_parser(programs):
    description = "pyMonteCarlo Command Line Interface. Quantify experimental " + \
                  "k-ratios using analytical or Monte Carlo programs from the " + \
                  "same interface. "
    epilog = "For more information, see http://pymontecarlo.sf.net"

    parser = OptionParser(usage="%prog [options] [measurement file]",
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
    parser.add_option("-m", '--max-iterations', dest="max_iterations", default=50, type="int",
                      help="Maximum number of iterations [default: %default]")
    parser.add_option("-l", '--convergence-limit', dest="convergence_limit", default=1e-5, type="float",
                      help="Convergence limit [default: %default]")

    # Iterator group
    group = OptionGroup(parser, "Iteration algorithm for quantification",
                        "Note: Specify only one of these flags.")

    group.add_option('--heinrich1972', dest='heinrich1972', action="store_true",
                     help='Heinrich hyperbolic iteration [default]')
    group.add_option('--pouchou1991', dest='pouchou1991', action="store_true",
                     help='Pouchou parabolic iteration')

    parser.add_option_group(group)

    # Program group
    group = OptionGroup(parser, "Monte Carlo programs",
                        "Note: Specify only one of these flags. Only supported programs are shown.")

    for alias in map(attrgetter('alias'), programs):
        group.add_option('--%s' % alias, dest=alias, action="store_true")

    parser.add_option_group(group)

    return parser

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

    quiet = values.quiet

    nbprocesses = values.nbprocesses
    if nbprocesses <= 0:
        parser.error("Number of processes must be greater than 0.")

    max_iterations = values.max_iterations
    if max_iterations < 1:
        raise ValueError, 'Maximum number of iterations must be greater or equal to 1'

    convergence_limit = values.convergence_limit
    if convergence_limit <= 0.0:
        raise ValueError, 'Convergence limit must be greater than 0.0'

    if values.pouchou1991:
        iterator_class = Pouchou1991Iterator
    else:
        iterator_class = Heinrich1972Iterator

    aliases = map(attrgetter('alias'), programs)
    selected_programs = [alias for alias in aliases if getattr(values, alias)]
    if not selected_programs:
        console.print_error("Please select one Monte Carlo program")
    if len(selected_programs) > 1:
        console.print_error("Please select only one Monte Carlo program")
    selected_program = selected_programs[0]

    if not args:
        console.print_error("Please specify a measurement file")
    if len(args) > 1:
        console.print_error("Please specify only one measurement file")
    try:
        measurement = Measurement.load(args[0])
    except Exception as ex:
        console.print_error(str(ex))

    # Setup
    workers = dict(zip(aliases, map(attrgetter('worker'), programs)))
    worker_class = workers[selected_program]

    runner = Runner(worker_class, outputdir, workdir, nbprocesses=nbprocesses)

    quant = Quantification(runner, iterator_class, measurement,
                           max_iterations, convergence_limit)

    progressbar = ProgressBar(console, max_iterations)
    if not quiet: progressbar.start()

    start_time = time.time()
    quant.start()

    try:
        while quant.is_alive():
            counter, progress, status = quant.report()
            if not quiet: progressbar.update(counter, progress, status)
            time.sleep(1)
    except Exception as ex:
        console.print_error('%s - %s' % (ex.__class__.__name__, str(ex)))

    quant.join()
    runner.join() # Not necessary, but cannot hurt
    if not quiet: progressbar.close()
    end_time = time.time()

    # Save compositions as CSV
    compositions = quant.get_compositions()
    zs = compositions[0].keys()

    filepath = os.path.join(outputdir, 'composition.csv')
    with open(filepath, 'w') as fp:
        writer = csv.writer(fp)

        writer.writerow(['iteration'] + zs)

        for i, composition in enumerate(compositions):
            writer.writerow([i + 1] + [composition[z] for z in zs])

    # Save statistics
    filepath = os.path.join(outputdir, 'stats.txt')
    with open(filepath, 'w') as fp:
        fp.write('time=%s\n' % (end_time - start_time))
        fp.write('iterations=%i\n' % quant.get_number_iterations())
        fp.write('program=%s\n' % selected_program)
        fp.write('convergenceLimit=%s\n' % convergence_limit)
        fp.write('maxIterations=%s\n' % max_iterations)
        fp.write('iteratorClass=%s\n' % iterator_class.__name__)

    # Print final results
    console.print_message("Element\tWeightFraction")
    console.print_line()

    composition = quant.get_last_composition()
    for z in sorted(composition.keys()):
        message = "%s\t%s" % (ep.symbol(z), composition[z])
        console.print_message(message)

    console.print_line()
    console.print_message("# of iterations: %i" % quant.get_number_iterations())

    # Clean up
    console.close()

if __name__ == '__main__':
    run()
