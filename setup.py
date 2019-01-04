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

ENTRY_POINTS = {'pymontecarlo.formats.hdf5':
                ['SettingsHDF5Handler = pymontecarlo.formats.hdf5.settings:SettingsHDF5Handler',
                 'SimulationHDF5Handler = pymontecarlo.formats.hdf5.simulation:SimulationHDF5Handler',
                 'ProjectHDF5Handler = pymontecarlo.formats.hdf5.project:ProjectHDF5Handler',

                 'XrayLineHDF5Handler = pymontecarlo.formats.hdf5.util.xrayline:XrayLineHDF5Handler',

                 'OptionsHDF5Handler = pymontecarlo.formats.hdf5.options.options:OptionsHDF5Handler',

                 'CylindricalBeamHDF5Handler = pymontecarlo.formats.hdf5.options.beam.cylindrical:CylindricalBeamHDF5Handler',
                 'GaussianBeamHDF5Handler = pymontecarlo.formats.hdf5.options.beam.gaussian:GaussianBeamHDF5Handler',

                 'MaterialHDF5Handler = pymontecarlo.formats.hdf5.options.material:MaterialHDF5Handler',
                 'VacuumHDF5Handler = pymontecarlo.formats.hdf5.options.material:VacuumHDF5Handler',
                 'LayerHDF5Handler = pymontecarlo.formats.hdf5.options.sample.base:LayerHDF5Handler',
                 'SubstrateSampleHDF5Handler = pymontecarlo.formats.hdf5.options.sample.substrate:SubstrateSampleHDF5Handler',
                 'InclusionSampleHDF5Handler = pymontecarlo.formats.hdf5.options.sample.inclusion:InclusionSampleHDF5Handler',
                 'HorizontalLayerSampleHDF5Handler = pymontecarlo.formats.hdf5.options.sample.horizontallayers:HorizontalLayerSampleHDF5Handler',
                 'VerticalLayerSampleHDF5Handler = pymontecarlo.formats.hdf5.options.sample.verticallayers:VerticalLayerSampleHDF5Handler',
                 'SphereSampleHDF5Handler = pymontecarlo.formats.hdf5.options.sample.sphere:SphereSampleHDF5Handler',

                 'PhotonDetectorHDF5Handler = pymontecarlo.formats.hdf5.options.detector.photon:PhotonDetectorHDF5Handler',

                 'PhotonIntensityAnalysisHDF5Handler = pymontecarlo.formats.hdf5.options.analysis.photonintensity:PhotonIntensityAnalysisHDF5Handler',
                 'KRatioAnalysisHDF5Handler = pymontecarlo.formats.hdf5.options.analysis.kratio:KRatioAnalysisHDF5Handler',

                 'BremsstrahlungEmissionModelHDF5Handler = pymontecarlo.formats.hdf5.options.model.bremsstrahlung_emission:BremsstrahlungEmissionModelHDF5Handler',
                 'DirectionCosineModelHDF5Handler = pymontecarlo.formats.hdf5.options.model.direction_cosine:DirectionCosineModelHDF5Handler',
                 'ElasticCrossSectionModelHDF5Handler = pymontecarlo.formats.hdf5.options.model.elastic_cross_section:ElasticCrossSectionModelHDF5Handler',
                 'EnergyLossModelHDF5Handler = pymontecarlo.formats.hdf5.options.model.energy_loss:EnergyLossModelHDF5Handler',
                 'FluorescenceModelHDF5Handler = pymontecarlo.formats.hdf5.options.model.fluorescence:FluorescenceModelHDF5Handler',
                 'InelasticCrossSectionModelHDF5Handler = pymontecarlo.formats.hdf5.options.model.inelastic_cross_section:InelasticCrossSectionModelHDF5Handler',
                 'IonizationCrossSectionModelHDF5Handler = pymontecarlo.formats.hdf5.options.model.ionization_cross_section:IonizationCrossSectionModelHDF5Handler',
                 'IonizationPotentialModelHDF5Handler = pymontecarlo.formats.hdf5.options.model.ionization_potential:IonizationPotentialModelHDF5Handler',
                 'MassAbsorptionCoefficientModelHDF5Handler = pymontecarlo.formats.hdf5.options.model.mass_absorption_coefficient:MassAbsorptionCoefficientModelHDF5Handler',
                 'PhotonScatteringCrossSectionModelHDF5Handler = pymontecarlo.formats.hdf5.options.model.photon_scattering_cross_section:PhotonScatteringCrossSectionModelHDF5Handler',
                 'RandomNumberGeneratorModelHDF5Handler = pymontecarlo.formats.hdf5.options.model.random_number_generator:RandomNumberGeneratorModelHDF5Handler',

                 'EmittedPhotonIntensityResultHDF5Handler = pymontecarlo.formats.hdf5.results.photonintensity:EmittedPhotonIntensityResultHDF5Handler',
                 'GeneratedPhotonIntensityResultHDF5Handler = pymontecarlo.formats.hdf5.results.photonintensity:GeneratedPhotonIntensityResultHDF5Handler',
                 'KRatioResultHDF5Handler = pymontecarlo.formats.hdf5.results.kratio:KRatioResultHDF5Handler',
                 ],

                'pymontecarlo.formats.series':
                [
                 'OptionsSeriesHandler = pymontecarlo.formats.series.options.options:OptionsSeriesHandler',

                 'CylindricalBeamSeriesHandler = pymontecarlo.formats.series.options.beam.cylindrical:CylindricalBeamSeriesHandler',
                 'GaussianBeamSeriesHandler = pymontecarlo.formats.series.options.beam.gaussian:GaussianBeamSeriesHandler',

                 'MaterialSeriesHandler = pymontecarlo.formats.series.options.material:MaterialSeriesHandler',
                 'VacuumSeriesHandler = pymontecarlo.formats.series.options.material:VacuumSeriesHandler',
                 'LayerSeriesHandler = pymontecarlo.formats.series.options.sample.base:LayerSeriesHandler',
                 'SubstrateSampleSeriesHandler = pymontecarlo.formats.series.options.sample.substrate:SubstrateSampleSeriesHandler',
                 'InclusionSampleSeriesHandler = pymontecarlo.formats.series.options.sample.inclusion:InclusionSampleSeriesHandler',
                 'HorizontalLayerSampleSeriesHandler = pymontecarlo.formats.series.options.sample.horizontallayers:HorizontalLayerSampleSeriesHandler',
                 'VerticalLayerSampleSeriesHandler = pymontecarlo.formats.series.options.sample.verticallayers:VerticalLayerSampleSeriesHandler',
                 'SphereSampleSeriesHandler = pymontecarlo.formats.series.options.sample.sphere:SphereSampleSeriesHandler',

                 'PhotonDetectorSeriesHandler = pymontecarlo.formats.series.options.detector.photon:PhotonDetectorSeriesHandler',

                 'PhotonIntensityAnalysisSeriesHandler = pymontecarlo.formats.series.options.analysis.photonintensity:PhotonIntensityAnalysisSeriesHandler',
                 'KRatioAnalysisSeriesHandler = pymontecarlo.formats.series.options.analysis.kratio:KRatioAnalysisSeriesHandler',

                 'ModelSeriesHandler = pymontecarlo.formats.series.options.model.base:ModelSeriesHandler',

                 'EmittedPhotonIntensityResultSeriesHandler = pymontecarlo.formats.series.results.photonintensity:EmittedPhotonIntensityResultSeriesHandler',
                 'GeneratedPhotonIntensityResultSeriesHandler = pymontecarlo.formats.series.results.photonintensity:GeneratedPhotonIntensityResultSeriesHandler',
                 'KRatioResultSeriesHandler = pymontecarlo.formats.series.results.kratio:KRatioResultSeriesHandler',
                 ],

                'pymontecarlo.formats.document':
                [
                 'OptionsDocumentHandler = pymontecarlo.formats.document.options.options:OptionsDocumentHandler',

                 'GaussianBeamDocumentHandler = pymontecarlo.formats.document.options.beam.gaussian:GaussianBeamDocumentHandler',
                 'CylindricalBeamDocumentHandler = pymontecarlo.formats.document.options.beam.cylindrical:CylindricalBeamDocumentHandler',

                 'MaterialDocumentHandler = pymontecarlo.formats.document.options.material:MaterialDocumentHandler',
                 'VacuumDocumentHandler = pymontecarlo.formats.document.options.material:VacuumDocumentHandler',
                 'LayerDocumentHandler = pymontecarlo.formats.document.options.sample.base:LayerDocumentHandler',
                 'SubstrateSampleDocumentHandler = pymontecarlo.formats.document.options.sample.substrate:SubstrateSampleDocumentHandler',
                 'InclusionSampleDocumentHandler = pymontecarlo.formats.document.options.sample.inclusion:InclusionSampleDocumentHandler',
                 'HorizontalLayerSampleDocumentHandler = pymontecarlo.formats.document.options.sample.horizontallayers:HorizontalLayerSampleDocumentHandler',
                 'VerticalLayerSampleDocumentHandler = pymontecarlo.formats.document.options.sample.verticallayers:VerticalLayerSampleDocumentHandler',
                 'SphereSampleDocumentHandler = pymontecarlo.formats.document.options.sample.sphere:SphereSampleDocumentHandler',

                 'PhotonDetectorDocumentHandler = pymontecarlo.formats.document.options.detector.photon:PhotonDetectorDocumentHandler',

                 'PhotonIntensityAnalysisDocumentHandler = pymontecarlo.formats.document.options.analysis.photonintensity:PhotonIntensityAnalysisDocumentHandler',
                 'KRatioAnalysisDocumentHandler = pymontecarlo.formats.document.options.analysis.kratio:KRatioAnalysisDocumentHandler',

                 'ModelDocumentHandler = pymontecarlo.formats.document.options.model.base:ModelDocumentHandler',
                 ]}

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

