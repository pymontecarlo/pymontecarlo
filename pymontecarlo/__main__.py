""""""

# Standard library modules.
import argparse
import multiprocessing
import logging
logger = logging.getLogger(__name__)

# Third party modules.
import tabulate

# Local modules.
import pymontecarlo
from pymontecarlo.util.cbook import find_by_type

# Globals and constants variables.

def _create_parser():
    usage = 'pymontecarlo'
    description = 'Run, configure pymontecarlo'
    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Run in debug mode')
    parser.add_argument('--programs', action='store_true',
                        help='List available and configured programs')

    return parser

def _create_commands(parser):
    subparsers = parser.add_subparsers(title='Commands', dest='command')
    _create_run_command(subparsers.add_parser('run'))
    _create_config_command(subparsers.add_parser('config'))

def _create_run_command(parser):
    parser.description = 'Run simulation(s) and save results in a project.'

    nprocessors = multiprocessing.cpu_count()

    parser.add_argument('-o', required=False, metavar='FILE',
                        help='Path to project')
    parser.add_argument('-s', action='store_true',
                        help='Skip existing simulations in project')
    parser.add_argument('-n', type=int, default=nprocessors,
                        help='Number of processors to use')

def _create_config_command(parser):
    parser.description = 'Configure pymontecarlo and Monte Carlo programs.'

    # Programs
    available_programs = dict((clasz.getname(), clasz)
                              for clasz in pymontecarlo.iter_available_programs())

    subparsers_programs = parser.add_subparsers(title='Programs', dest='program')
    for name, clasz in sorted(available_programs.items()):
        parser_program = subparsers_programs.add_parser(name)

        try:
            clasz.prepare_parser(parser_program)
        except:
            logger.exception('Prepare parser failed')
            subparsers_programs._name_parser_map.pop(name)

def _parse(ns):
    if ns.verbose:
        logger.setLevel(logging.DEBUG)

    if ns.programs:
        available_programs = \
            set(clasz.getname() for clasz in pymontecarlo.iter_available_programs())
        configured_programs = \
            dict((p.getname(), p) for p in pymontecarlo.settings.programs)

        header = ['Program', 'Available', 'Configured', 'Details']
        rows = []
        for name in sorted(available_programs):
            configured = name in configured_programs
            if configured:
                program_namespace = configured_programs[name].namespace
                details = ['{}: {}'.format(k, v)
                           for k, v in program_namespace.__dict__.items()]
            else:
                details = []
            rows.append([name, True, configured, ', '.join(details)])

        print(tabulate.tabulate(rows, header))
        return

def _parse_commands(ns):
    if ns.command == 'run':
        _parse_run_command(ns)

    if ns.command == 'config':
        _parse_config_command(ns)

def _parse_run_command(ns):
    pass

def _parse_config_command(ns):
    if ns.program:
        available_programs = dict(pymontecarlo.iter_available_programs())

        # Create program
        name = ns.program
        clasz = available_programs[name]
        program = clasz.from_namespace(ns)

        # Remove existing program
        configured_programs = pymontecarlo.settings.programs
        for configured_program in find_by_type(configured_programs, clasz):
            pymontecarlo.settings.programs.remove(configured_program)

        # Add new program
        pymontecarlo.settings.programs.append(program)

    # Save settings
    pymontecarlo.settings.write()
    print('Settings updated and saved')

def main():
    parser = _create_parser()
    _create_commands(parser)

    ns = parser.parse_args()
    print(ns)
    _parse(ns)
    _parse_commands(ns)

if __name__ == '__main__':
    main()
