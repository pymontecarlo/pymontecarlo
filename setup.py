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

SETUP_REQUIRES = ['setuptools']
INSTALL_REQUIRES = ['pyparsing>=2.0.0', 'numpy', 'h5py', 'pyxray>=1.0.1',
                    'more_itertools>=2.5.0', 'pint', 'uncertainties',
                    'matplotlib']
TESTS_REQUIRE = ['nose', 'coverage']
EXTRAS_REQUIRE = {'doc': ['docutils', 'jinja2', 'sphinx', 'pybtex']}

CMDCLASS = versioneer.get_cmdclass()

ENTRY_POINTS = {'pymontecarlo.program': []}

setup(name="pyMonteCarlo",
      version=versioneer.get_version(),
      url='https://github.com/pymontecarlo',
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

      packages=PACKAGES,

      setup_requires=SETUP_REQUIRES,
      install_requires=INSTALL_REQUIRES,
      tests_require=TESTS_REQUIRE,
      extras_require=EXTRAS_REQUIRE,

      cmdclass=CMDCLASS,

      entry_points=ENTRY_POINTS,

      test_suite='nose.collector',
)

