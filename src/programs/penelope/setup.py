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
from pymontecarlo.util.dist.command import clean
from pymontecarlo.program._penelope.util.dist.command import \
    bdist_deb_pendbase, bdist_deb_material
from pymontecarlo.program.penepma.util.dist.command import \
    bdist_deb_penepma

# Globals and constants variables.

setup(name="pyMonteCarlo-PENELOPE",
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

      packages=['pymontecarlo',
                'pymontecarlo.program',
                'pymontecarlo.program._penelope',
                'pymontecarlo.program._penelope.options',
                'pymontecarlo.program.penepma',
                'pymontecarlo.program.penepma.options',
                'pymontecarlo.program.penshower'],

      install_requires=['penelopelib>=0.1'],
      dependency_links=["https://bitbucket.org/pymontecarlo/pymontecarlo/downloads"],

      cmdclass={'clean': clean,
                'bdist_deb_pendbase': bdist_deb_pendbase,
                'bdist_deb_material': bdist_deb_material,
                'bdist_deb_penepma': bdist_deb_penepma},

      entry_points={'pymontecarlo.program':
                        ['penepma=pymontecarlo.program.penepma.config:program',
                         'penshower=pymontecarlo.program.penshower.config:program'],
                    'pymontecarlo.program.cli':
                        ['penepma=pymontecarlo.program.penepma.config_cli:cli',
                         'penshower=pymontecarlo.program.penshower.config_cli:cli'],
                    'pymontecarlo.program.gui':
                        ['penepma=pymontecarlo.program.penepma.config_gui:gui',
                         'penshower=pymontecarlo.program.penshower.config_gui:gui'], },

      test_suite='nose.collector',
)

