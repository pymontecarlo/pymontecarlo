#!/usr/bin/env python

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import sys
sys.path.insert(0, '/home/ppinard/documents/workspace/pydev/bbfreeze')

# Third party modules.
import bbfreeze
print bbfreeze.__file__
from setuptools import setup

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
package_data = {'pymontecarlo.util': ['data/*']}

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
      package_data=package_data,

      cmdclass={'clean': clean},

      setup_requires=['nose>=1.0'],
      install_requires=['pyparsing >=1.5.2, <2.0', 'numpy>=1.6.1',
                        'h5py>=2.0.1', 'matplotlib>=1.1'],

      namespace_packages=['pymontecarlo', 'pymontecarlo.program'],

      entry_points={'console_scripts':
                    ['pymontecarlo-configure = pymontecarlo.ui.cli.configure:run',
                     'pymontecarlo-cli = pymontecarlo.ui.cli.main:run', ]},

      command_options={'bdist_bbfreeze': {'include_py': (None, True)}},

      test_suite='nose.collector',
)

