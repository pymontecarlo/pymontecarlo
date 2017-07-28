""""""

# Standard library modules.
import os
import argparse
import multiprocessing
import logging
logger = logging.getLogger(__name__)

# Third party modules.

# Local modules.
from pymontecarlo.util.entrypoint import resolve_entrypoints, ENTRYPOINT_PROGRAMS

# Globals and constants variables.

def _create_parser():
    prog = 'pymontecarlo'
    description = 'Run simulations from the command line'
    parser = argparse.ArgumentParser(prog=prog, description=description)

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Run in debug mode')

    parser.add_argument('--programs', action='store_true',
                        help='List available programs')

    parser.add_argument('-o', required=False, metavar='FILE',
                        help='Path to project')

    parser.add_argument('-s', action='store_true',
                        help='Skip existing simulations in project')

    nprocessors = multiprocessing.cpu_count()
    parser.add_argument('-n', type=int, default=nprocessors,
                        help='Number of processors to use')

    return parser

def _parse(parser, ns):
    if ns.verbose:
        logger.setLevel(logging.DEBUG)

    if ns.programs:
        programs = sorted(resolve_entrypoints(ENTRYPOINT_PROGRAMS).keys())
        parser.exit(message='Programs: ' + ', '.join(programs) + os.linesep)

def main():
    parser = _create_parser()

    ns = parser.parse_args()

    _parse(parser, ns)
    parser.print_help()

if __name__ == '__main__':
    main()
