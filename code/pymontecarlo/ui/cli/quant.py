#!/usr/bin/env python
"""
================================================================================
:mod:`quant` -- Quantification of experimental results
================================================================================

.. module:: quant
   :synopsis: Quantification of experimental results

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
import glob
from operator import attrgetter
from optparse import OptionParser, OptionGroup

# Third party modules.

# Local modules.
from pymontecarlo import get_programs

from pymontecarlo.quant.input.measurement import Measurement
from pymontecarlo.quant.runner.runner import Runner
from pymontecarlo.quant.runner.iterator import \
    (SimpleIterator, Heinrich1972Iterator, Pouchou1991Iterator,
     Wegstein1958Iterator)
from pymontecarlo.quant.runner.convergor import \
    CompositionConvergor, KRatioConvergor
from pymontecarlo.quant.runner.calculator import SimpleCalculator

from pymontecarlo.ui.cli.console import create_console, ProgressBar

# Globals and constants variables.

def create_parser(programs):
    description = "pyMonteCarlo Command Line Interface. Quantify experimental " + \
                  "k-ratios using analytical or Monte Carlo programs from the " + \
                  "same interface. "
    epilog = "For more information, see http://pymontecarlo.sf.net"

    parser = OptionParser(usage="%prog [options] [measurement files...]",
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
    parser.add_option('-s', '--skip', dest='skip', default=False,
                      action='store_true', help='Skip quantification if results already exist')

    # Iterator group
    group = OptionGroup(parser, "Iteration algorithm for quantification",
                        "Note: Specify only one of these flags.")

    group.add_option('--linear', dest='linear', action="store_true",
                     help='Simple linear iteration')
    group.add_option('--heinrich1972', dest='heinrich1972', action="store_true",
                     help='Heinrich hyperbolic iteration [default]')
    group.add_option('--pouchou1991', dest='pouchou1991', action="store_true",
                     help='Pouchou parabolic iteration')
    group.add_option('--wegstein1958', dest='wegstein1958', action="store_true",
                     help='Wegstein iteration')

    parser.add_option_group(group)

    # Convergor group
    group = OptionGroup(parser, "Convergence algorithm for quantification",
                        "Note: Specify only one of these flags.")

    group.add_option('--composition', dest='composition', action="store_true",
                     help='Check convergence with composition [default]')
    group.add_option('--kratio', dest='kratio', action="store_true",
                     help='Check convergence with k-ratio')

    parser.add_option_group(group)

    # Calculator group
    group = OptionGroup(parser, "Algorithm to calculate k-ratio",
                        "Note: Specify only one of these flags.")

    group.add_option('--simple', dest='simple', action="store_true",
                     help='Simple ratio between unknown and standard intensities [default]')

    parser.add_option_group(group)

    # Program group
    group = OptionGroup(parser, "Monte Carlo programs",
                        "Note: Specify only one of these flags. Only supported programs are shown.")

    for alias in map(attrgetter('alias'), programs):
        group.add_option('--%s' % alias, dest=alias, action="store_true")

    parser.add_option_group(group)

    return parser

def load_measurements(filepaths, measurements=[]):
    for filepath in filepaths:
        if os.path.isdir(filepath):
            load_measurements(glob.glob(os.path.join(filepath, '*.xml')), measurements)
            measurements.sort()
            return

        measurements.append(Measurement.load(filepath))

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

    overwrite = not values.skip

    max_iterations = values.max_iterations
    if max_iterations < 1:
        raise ValueError, 'Maximum number of iterations must be greater or equal to 1'

    convergence_limit = values.convergence_limit
    if convergence_limit <= 0.0:
        raise ValueError, 'Convergence limit must be greater than 0.0'

    if values.linear:
        iterator_class = SimpleIterator
    elif values.pouchou1991:
        iterator_class = Pouchou1991Iterator
    elif values.wegstein1958:
        iterator_class = Wegstein1958Iterator
    else:
        iterator_class = Heinrich1972Iterator

    if values.kratio:
        convergor_class = KRatioConvergor
    else:
        convergor_class = CompositionConvergor

    if values.simple:
        calculator_class = SimpleCalculator
    else:
        calculator_class = SimpleCalculator

    aliases = map(attrgetter('alias'), programs)
    selected_programs = [alias for alias in aliases if getattr(values, alias)]
    if not selected_programs:
        console.print_error("Please select one Monte Carlo program")
    if len(selected_programs) > 1:
        console.print_error("Please select only one Monte Carlo program")
    selected_program = selected_programs[0]

    workers = dict(zip(aliases, map(attrgetter('worker'), programs)))
    worker_class = workers[selected_program]

    measurements = []
    try:
        load_measurements(args, measurements)
    except Exception as ex:
        console.print_error(str(ex))

    if not measurements:
        console.print_error("Please specify a measurement file")

    # Setup
    runner = Runner(worker_class, iterator_class, convergor_class, calculator_class,
                    outputdir, workdir,
                    overwrite, max_iterations, nbprocesses,
                    limit=convergence_limit)

    progressbar = ProgressBar(console, len(measurements))
    if not quiet: progressbar.start()

    runner.start()

    for measurement in measurements:
        runner.put(measurement)

    try:
        while runner.is_alive():
            counter, progress, status = runner.report()
            if not quiet: progressbar.update(counter, progress, status)
            time.sleep(1)
    except Exception as ex:
        console.print_error('%s - %s' % (ex.__class__.__name__, str(ex)))

    runner.stop()
    if not quiet: progressbar.close()

    # Clean up
    console.close()

if __name__ == '__main__':
    run()
