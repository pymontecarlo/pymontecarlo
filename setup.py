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
                    'matplotlib', 'tabulate']
EXTRAS_REQUIRE = {'develop': ['nose', 'coverage', 'docutils', 'jinja2', 'sphinx', 'pybtex']}

CMDCLASS = versioneer.get_cmdclass()

ENTRY_POINTS = {'pymontecarlo.program': [],

                'pymontecarlo.fileformat':
                ['SettingsHDF5Handler = pymontecarlo.fileformat.settings:SettingsHDF5Handler',

                 'XrayLineHDF5Handler = pymontecarlo.fileformat.util.xrayline:XrayLineHDF5Handler',

                 'GaussianBeamHDF5Handler = pymontecarlo.fileformat.options.beam.gaussian:GaussianBeamHDF5Handler',

                 'MaterialHDF5Handler = pymontecarlo.fileformat.options.material:MaterialHDF5Handler',
                 'LayerHDF5Handler = pymontecarlo.fileformat.options.sample.base:LayerHDF5Handler',
                 'SubstrateSampleHDF5Handler = pymontecarlo.fileformat.options.sample.substrate:SubstrateSampleHDF5Handler',
                 'InclusionSampleHDF5Handler = pymontecarlo.fileformat.options.sample.inclusion:InclusionSampleHDF5Handler',
                 'HorizontalLayerSampleHDF5Handler = pymontecarlo.fileformat.options.sample.horizontallayers:HorizontalLayerSampleHDF5Handler',
                 'VerticalLayerSampleHDF5Handler = pymontecarlo.fileformat.options.sample.verticallayers:VerticalLayerSampleHDF5Handler',
                 'SphereSampleHDF5Handler = pymontecarlo.fileformat.options.sample.sphere:SphereSampleHDF5Handler',

                 'PhotonDetectorHDF5Handler = pymontecarlo.fileformat.options.detector.photon:PhotonDetectorHDF5Handler',

                 'ShowersLimitHDF5Handler = pymontecarlo.fileformat.options.limit.showers:ShowersLimitHDF5Handler',
                 'UncertaintyLimitHDF5Handler = pymontecarlo.fileformat.options.limit.uncertainty:UncertaintyLimitHDF5Handler',
                 ]}

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

      install_requires=INSTALL_REQUIRES,
      extras_require=EXTRAS_REQUIRE,

      cmdclass=CMDCLASS,

      entry_points=ENTRY_POINTS,

      test_suite='nose.collector',
)

