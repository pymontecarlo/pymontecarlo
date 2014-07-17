#!/usr/bin/env python

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import codecs
import re

# Third party modules.
from setuptools import setup, find_packages

# Local modules.
from pymontecarlo.util.dist.command.clean import clean
from pymontecarlo.util.dist.command.check import check

# Globals and constants variables.
BASEDIR = os.path.abspath(os.path.dirname(__file__))

def find_version(*file_paths):
    """
    Read the version number from a source file.

    .. note::

       Why read it, and not import?
       see https://groups.google.com/d/topic/pypa-dev/0PkjVpcxTzQ/discussion
    """
    # Open in Latin-1 so that we avoid encoding errors.
    # Use codecs.open for Python 2 compatibility
    with codecs.open(os.path.join(BASEDIR, *file_paths), 'r', 'latin1') as f:
        version_file = f.read()

    # The version line must have the form
    # __version__ = 'ver'
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

packages = find_packages(exclude=('pymontecarlo.util.dist*',))
namespace_packages = ['pymontecarlo',
                      'pymontecarlo.program',
                      'pymontecarlo.ui']
requirements = ['pyparsing', 'numpy', 'h5py', 'pyxray']

entry_points = {'pymontecarlo.fileformat.options.material':
                    ['Material = pymontecarlo.fileformat.options.material:MaterialXMLHandler'],
                'pymontecarlo.fileformat.options.beam':
                    ['PencilBeam = pymontecarlo.fileformat.options.beam:PencilBeamXMLHandler',
                     'GaussianBeam = pymontecarlo.fileformat.options.beam:GaussianBeamXMLHandler', ],
                'pymontecarlo.fileformat.options.geometry':
                    ['Substrate = pymontecarlo.fileformat.options.geometry:SubstrateXMLHandler',
                     'Inclusion = pymontecarlo.fileformat.options.geometry:InclusionXMLHandler',
                     'HorizontalLayers = pymontecarlo.fileformat.options.geometry:HorizontalLayersXMLHandler',
                     'VerticalLayers = pymontecarlo.fileformat.options.geometry:VerticalLayersXMLHandler',
                     'Sphere = pymontecarlo.fileformat.options.geometry:SphereXMLHandler'],
                'pymontecarlo.fileformat.options.detector':
                    ['BackscatteredElectronEnergyDetector = pymontecarlo.fileformat.options.detector:BackscatteredElectronEnergyDetectorXMLHandler',
                     'TransmittedElectronEnergyDetector = pymontecarlo.fileformat.options.detector:TransmittedElectronEnergyDetectorXMLHandler',
                     'BackscatteredElectronPolarAngularDetector = pymontecarlo.fileformat.options.detector:BackscatteredElectronPolarAngularDetectorXMLHandler',
                     'TransmittedElectronPolarAngularDetector = pymontecarlo.fileformat.options.detector:TransmittedElectronPolarAngularDetectorXMLHandler',
                     'BackscatteredElectronAzimuthalAngularDetector = pymontecarlo.fileformat.options.detector:BackscatteredElectronAzimuthalAngularDetectorXMLHandler',
                     'TransmittedElectronAzimuthalAngularDetector = pymontecarlo.fileformat.options.detector:TransmittedElectronAzimuthalAngularDetectorXMLHandler',
                     'BackscatteredElectronRadialDetector = pymontecarlo.fileformat.options.detector:BackscatteredElectronRadialDetectorXMLHandler',
                     'PhotonSpectrumDetector = pymontecarlo.fileformat.options.detector:PhotonSpectrumDetectorXMLHandler',
                     'PhotonDepthDetector = pymontecarlo.fileformat.options.detector:PhotonDepthDetectorXMLHandler',
                     'PhiZDetector = pymontecarlo.fileformat.options.detector:PhiZDetectorXMLHandler',
                     'PhotonRadialDetector = pymontecarlo.fileformat.options.detector:PhotonRadialDetectorXMLHandler',
                     'PhotonEmissionMapDetector = pymontecarlo.fileformat.options.detector:PhotonEmissionMapDetectorXMLHandler',
                     'PhotonIntensityDetector = pymontecarlo.fileformat.options.detector:PhotonIntensityDetectorXMLHandler',
                     'TimeDetector = pymontecarlo.fileformat.options.detector:TimeDetectorXMLHandler',
                     'ElectronFractionDetector = pymontecarlo.fileformat.options.detector:ElectronFractionDetectorXMLHandler',
                     'ShowersStatisticsDetector = pymontecarlo.fileformat.options.detector:ShowersStatisticsDetectorXMLHandler',
                     'TrajectoryDetector = pymontecarlo.fileformat.options.detector:TrajectoryDetectorXMLHandler', ],
                'pymontecarlo.fileformat.options.limit':
                    ['TimeLimit = pymontecarlo.fileformat.options.limit:TimeLimitXMLHandler',
                     'ShowersLimit = pymontecarlo.fileformat.options.limit:ShowersLimitXMLHandler',
                     'UncertaintyLimit = pymontecarlo.fileformat.options.limit:UncertaintyLimitXMLHandler'],
                'pymontecarlo.fileformat.options.model':
                    ['Model = pymontecarlo.fileformat.options.model:ModelXMLHandler'],

                'pymontecarlo.fileformat.results.result':
                    ['PhotonIntensityResult = pymontecarlo.fileformat.results.result:PhotonIntensityResultHDF5Handler',
                     'PhotonSpectrumResult = pymontecarlo.fileformat.results.result:PhotonSpectrumResultHDF5Handler',
                     'PhotonDepthResult = pymontecarlo.fileformat.results.result:PhotonDepthResultHDF5Handler',
                     'PhiZResult = pymontecarlo.fileformat.results.result:PhiZResultHDF5Handler',
                     'PhotonRadialResult = pymontecarlo.fileformat.results.result:PhotonRadialResultHDF5Handler',
                     'PhotonEmissionMapResult = pymontecarlo.fileformat.results.result:PhotonEmissionMapResultHDF5Handler',
                     'TimeResult = pymontecarlo.fileformat.results.result:TimeResultHDF5Handler',
                     'ShowersStatisticsResult = pymontecarlo.fileformat.results.result:ShowersStatisticsResultHDF5Handler',
                     'ElectronFractionResult = pymontecarlo.fileformat.results.result:ElectronFractionResultHDF5Handler',
                     'TrajectoryResult = pymontecarlo.fileformat.results.result:TrajectoryResultHDF5Handler',
                     'BackscatteredElectronEnergyResult = pymontecarlo.fileformat.results.result:BackscatteredElectronEnergyResultHDF5Handler',
                     'TransmittedElectronEnergyResult = pymontecarlo.fileformat.results.result:TransmittedElectronEnergyResultHDF5Handler',
                     'BackscatteredElectronAzimuthalAngularResult = pymontecarlo.fileformat.results.result:BackscatteredElectronAzimuthalAngularResultHDF5Handler',
                     'TransmittedElectronAzimuthalAngularResult = pymontecarlo.fileformat.results.result:TransmittedElectronAzimuthalAngularResultHDF5Handler',
                     'BackscatteredElectronPolarAngularResult = pymontecarlo.fileformat.results.result:BackscatteredElectronPolarAngularResultHDF5Handler',
                     'TransmittedElectronPolarAngularResult = pymontecarlo.fileformat.results.result:TransmittedElectronPolarAngularResultHDF5Handler',
                     'BackscatteredElectronRadialResult = pymontecarlo.fileformat.results.result:BackscatteredElectronRadialResultHDF5Handler', ],
                }

setup(name="pyMonteCarlo",
      version=find_version('pymontecarlo', '__init__.py'),
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
      namespace_packages=namespace_packages,

      cmdclass={'clean': clean, "check": check},

      setup_requires=['nose'],
      install_requires=requirements,

      entry_points=entry_points,

      test_suite='nose.collector',
)

