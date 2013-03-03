#!/usr/bin/env python

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.
from setuptools import setup

# Local modules.
from pymontecarlo.util.dist.command import build_py, clean

# Globals and constants variables.

setup(name="pyMonteCarlo-NISTMonte",
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

      packages=['pymontecarlo.program.nistmonte',
                'pymontecarlo.program.nistmonte.input',
                'pymontecarlo.program.nistmonte.runner'],
      package_dir={'pymontecarlo': '../../../pymontecarlo'},

      cmdclass={'build_py': build_py, 'clean': clean},

      entry_points={'pymontecarlo.program':
                        'nistmonte=pymontecarlo.program.nistmonte.config:program',
                    'pymontecarlo.program.cli':
                        'nistmonte=pymontecarlo.program.nistmonte.config_cli:cli',
                    'pymontecarlo.program.gui':
                        'nistmonte=pymontecarlo.program.nistmonte.config_gui:gui', }
)

