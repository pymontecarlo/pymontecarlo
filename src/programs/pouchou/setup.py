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

# Globals and constants variables.

setup(name="pyMonteCarlo-Pouchou",
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

      packages=['pymontecarlo.program._pouchou',
                'pymontecarlo.program._pouchou.input',
                'pymontecarlo.program._pouchou.runner',
                'pymontecarlo.program.pap',
                'pymontecarlo.program.pap.runner',
                'pymontecarlo.program.xpp',
                'pymontecarlo.program.xpp.runner'],
      package_data={'pymontecarlo.program._pouchou': ['data/*']},

      install_requires=['PouchouPichoirModels>=0.1'],
      dependency_links=["https://bitbucket.org/pymontecarlo/pymontecarlo/downloads"],

      cmdclass={'clean': clean},

      entry_points={'pymontecarlo.program':
                        'pap=pymontecarlo.program.pap.config:program',
                    'pymontecarlo.program.cli':
                        'pap=pymontecarlo.program.pap.config_cli:cli',
                    'pymontecarlo.program.gui':
                        'pap=pymontecarlo.program.pap.config_gui:gui',
                    'pymontecarlo.program':
                        'xpp=pymontecarlo.program.xpp.config:program',
                    'pymontecarlo.program.cli':
                        'xpp=pymontecarlo.program.xpp.config_cli:cli',
                    'pymontecarlo.program.gui':
                        'xpp=pymontecarlo.program.xpp.config_gui:gui', }
)

