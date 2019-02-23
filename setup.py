#!/usr/bin/env python

# Standard library modules.
import os

# Third party modules.
from setuptools import setup, find_packages

# Local modules.
import versioneer


# Globals and constants variables.
BASEDIR = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(BASEDIR, 'README.rst'), 'r') as fp:
    LONG_DESCRIPTION = fp.read()

PACKAGES = find_packages()

INSTALL_REQUIRES = ['pyparsing', 'numpy', 'h5py', 'pyxray',
                    'more_itertools', 'pint', 'uncertainties',
                    'matplotlib', 'tabulate', 'psutil', 'pandas',
                    'docutils', 'tqdm']
EXTRAS_REQUIRE = {'develop': ['pytest', 'pytest-cov', 'pytest-asyncio',
                              'nose', 'coverage', 'docutils', 'jinja2',
                              'sphinx', 'pybtex', 'sphinx_rtd_theme']}

CMDCLASS = versioneer.get_cmdclass()

ENTRY_POINTS = {}

setup(name="pyMonteCarlo",
      version=versioneer.get_version(),
      url='https://github.com/pymontecarlo',
      description="Python interface for Monte Carlo simulation programs",
      author="Philippe T. Pinard, Hendrix Demers, Raynald Gauvin and Silvia Richter",
      author_email="philippe.pinard@gmail.com",
      maintainer="Philippe T. Pinard",
      maintainer_email="philippe.pinard@gmail.com",
      license="Apache License version 2.0",
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: End Users/Desktop',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Natural Language :: English',
                   'Programming Language :: Python',
                   'Operating System :: OS Independent',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Scientific/Engineering :: Physics'],

      packages=PACKAGES,

      install_requires=INSTALL_REQUIRES,
      extras_require=EXTRAS_REQUIRE,

      cmdclass=CMDCLASS,

      entry_points=ENTRY_POINTS,

      test_suite='nose.collector',
)

