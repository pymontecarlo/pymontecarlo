#!/usr/bin/env python

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os

# Third party modules.
from setuptools import setup, find_packages

# Local modules.
from pymontecarlo.util.dist.command.clean import clean
from pymontecarlo.util.dist.command.check import check

import versioneer

# Globals and constants variables.
BASEDIR = os.path.abspath(os.path.dirname(__file__))

packages = find_packages(exclude=('pymontecarlo.util.dist*',))
namespace_packages = ['pymontecarlo',
                      'pymontecarlo.program',
                      'pymontecarlo.ui']
requirements = ['pyparsing', 'numpy', 'h5py', 'pyxray']

entry_points = {'pymontecarlo.fileformat.options.material':
                    ['Material = pymontecarlo.fileformat.options.material:MaterialXMLHandler'],
                'pymontecarlo.fileformat.options.beam':
                    ['PencilBeam = pymontecarlo.fileformat.options.beam:PencilBeamXMLHandler',
                     'GaussianBeam = pymontecarlo.fileformat.options.beam:GaussianBeamXMLHandler',
                     'GaussianExpTailBeam = pymontecarlo.fileformat.options.beam:GaussianExpTailBeamXMLHandler', ],
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
                    ['RegisteredModel = pymontecarlo.fileformat.options.model:RegisteredModelXMLHandler',
                     'UserDefinedMassAbsorptionCoefficientModel = pymontecarlo.fileformat.options.model:UserDefinedMassAbsorptionCoefficientModelXMLHandler'],

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

CMDCLASS = versioneer.get_cmdclass()
CMDCLASS['clean'] = clean
CMDCLASS["check"] = check

setup(name="pyMonteCarlo",
      version=versioneer.get_version(),
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

      cmdclass=CMDCLASS,

      setup_requires=['nose'],
      install_requires=requirements,

      entry_points=entry_points,

      test_suite='nose.collector',
)

