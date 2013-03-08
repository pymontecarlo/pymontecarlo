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

# Third party modules.
from setuptools import setup
from cx_Freeze.dist import Distribution, build, build_exe
from cx_Freeze.freezer import Executable

# Local modules.
from pymontecarlo.util.dist.command import clean

# Globals and constants variables.

packages = ['pymontecarlo',
            'pymontecarlo.input',
            'pymontecarlo.output',
            'pymontecarlo.program',
            'pymontecarlo.runner',
            'pymontecarlo.ui',
            'pymontecarlo.ui.cli',
            'pymontecarlo.util']

namespace_packages = ['pymontecarlo',
                      'pymontecarlo.program']

build_exe_options = {"packages": packages,
                     "namespace_packages": namespace_packages,
                     "excludes": ["Tkinter"],
                     "includes": ["wx", "wx.lib.pubsub"],
                     "init_script": os.path.abspath('initscripts/Console.py')}

cli_executables = {'pymontecarlo-configure': 'pymontecarlo.ui.cli.configure:run',
                   'pymontecarlo-cli': 'pymontecarlo.ui.cli.main:run'}
gui_executables = {'pymontecarlo': 'pymontecarlo.ui.gui.main:run'}

entry_points = {}
entry_points['console_scripts'] = \
    ['%s = %s' % item for item in cli_executables.items()]
entry_points['gui_scripts'] = \
    ['%s = %s' % item for item in gui_executables.items()]

def _make_executable(target_name, script, gui=False):
    path = os.path.join(*script.split(":")[0].split('.')) + '.py'
    if sys.platform == "win32": target_name += '.exe'
    base = "Win32GUI" if sys.platform == "win32" and gui else None
    return Executable(path, targetName=target_name, base=base)

executables = []
for target_name, script in cli_executables.items():
    executables.append(_make_executable(target_name, script, False))
for target_name, script in gui_executables.items():
    executables.append(_make_executable(target_name, script, True))

setup(name="pyMonteCarlo",
      version='0.1',
      url='http://pymontecarlo.bitbucket.org',
      description="Python interface for Monte Carlo simulation programs",
      author="Hendrix Demers and Philippe T. Pinard",
      author_email="hendrix.demers@mail.mcgill.ca and philippe.pinard@gmail.com",
      license="GPL v3",
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: End Users/Desktop',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Natural Language :: English',
                   'Programming Language :: Python',
                   'Operating System :: OS Independent',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Scientific/Engineering :: Physics'],

      packages=packages,
      package_data={'pymontecarlo.util': ['data/*']},
      namespace_packages=namespace_packages,

      distclass=Distribution,
      cmdclass={'clean': clean, "build": build, "build_exe": build_exe},

      setup_requires=['nose>=1.0'],
      install_requires=['pyparsing >=1.5.2, <2.0', 'numpy>=1.5',
                        'h5py>=2.0.1', 'matplotlib>=1.1'],

      entry_points=entry_points,
      executables=executables,

      options={"build_exe": build_exe_options},

      test_suite='nose.collector',
)

