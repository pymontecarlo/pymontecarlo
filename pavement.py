#!/usr/bin/env python

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import sys
import glob
from ConfigParser import SafeConfigParser
from subprocess import check_call

# Third party modules.
from paver.easy import task, cmdopts

# Local modules.

# Globals and constants variables.

# Read configuration
_configfilepath = os.path.join(os.path.dirname(__file__), 'pavement.cfg')
if not os.path.exists(_configfilepath):
    raise IOError, 'No configuration "pavement.cfg" found'

config = SafeConfigParser()
config.read(_configfilepath)

def _call_setup(filepath, *args):
    filepath = os.path.abspath(filepath)
    cwd = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    process_args = ('python', filename) + args

    print '--Running %s' % os.path.relpath(filepath, os.curdir)
    check_call(process_args, cwd=cwd)

def _call_core_setup(*args):
    """
    Calls setup.py of core.
    """
    _call_setup(os.path.join('src', 'core', 'setup.py'), *args)

def _call_program_setups(*args):
    """
    Calls setup.py of all programs.
    """
    for setup_path in glob.glob(os.path.join('src', 'programs', '*', 'setup.py')):
        _call_setup(setup_path, *args)

def _call_dependency_setups(*args):
    """
    Calls setup.py of all dependencies.
    """
    # casinoTools
    projectdir = config.get('projects', 'casinoTools')
    filepath = os.path.join(projectdir, 'setup_casino2.py')
    _call_setup(filepath, *args)

    # winxrayTools
    projectdir = config.get('projects', 'winxrayTools')
    filepath = os.path.join(projectdir, 'setup.py')
    _call_setup(filepath, *args)

    # PouchouPichoirModels
    projectdir = config.get('projects', 'PouchouPichoirModels')
    filepath = os.path.join(projectdir, 'setup.py')
    _call_setup(filepath, *args)

    # PENELOPE
    projectdir = config.get('projects', 'penelope')
    filepath = os.path.join(projectdir, 'setup.py')
    _call_setup(filepath, *args)

def _call_all_setups(*args):
    """
    Calls setup.py of pymontecarlo core and all programs.
    """
    _call_dependency_setups(*args)
    _call_core_setup(*args)
    _call_program_setups(*args)

@task
def clean():
    """
    Cleans all build output from pymontecarlo and programs.
    """
    _call_all_setups('clean', '--all')

@task
def purge():
    """
    Cleans all build and dist output from pymontecarlo and programs.
    """
    # NOTE: Dependencies do not have purge option
    _call_core_setup(*args)
    _call_program_setups(*args)

@task
@cmdopts([('uninstall', 'u', 'Uninstall development mode'),
          ('prefix=', '', 'Prefix for installation')])
def develop(options):
    """
    Registers all programs as development mode.
    """
    args = []
    uninstall = hasattr(options, 'uninstall')
    if uninstall: args.append('-u')
    if hasattr(options, 'prefix'): args.extend(['--prefix', options.prefix])

    # Dependencies
    _call_dependency_setups('develop', *args)

    # Core and programs
    if not uninstall:
        _call_core_setup('develop', *args)
        _call_program_setups('develop', *args)
    else:
        _call_program_setups('develop', *args)
        _call_core_setup('develop', *args)

@task
def sdist():
    """
    Builds source distribution from pymontecarlo and programs.
    """
    dist_dir = os.path.abspath(os.path.join(os.curdir, 'dist'))
    _call_all_setups('bdist_egg', '-d', dist_dir)

@task
def bdist_egg():
    """
    Builds egg distribution from pymontecarlo and programs.
    """
    dist_dir = os.path.abspath(os.path.join(os.curdir, 'dist'))
    _call_all_setups('bdist_egg', '-d', dist_dir)

@task
def test():
    """
    Tests all
    """
    _call_all_setups('test')
