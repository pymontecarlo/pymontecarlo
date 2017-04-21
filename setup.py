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
                    'matplotlib', 'tabulate', 'psutil']
EXTRAS_REQUIRE = {'develop': ['nose', 'coverage', 'docutils', 'jinja2', 'sphinx', 'pybtex']}

CMDCLASS = versioneer.get_cmdclass()

ENTRY_POINTS = {'pymontecarlo.program': [],

                'pymontecarlo.formats.hdf5':
                ['SettingsHDF5Handler = pymontecarlo.formats.hdf5.settings:SettingsHDF5Handler',
                 'SimulationHDF5Handler = pymontecarlo.formats.hdf5.simulation:SimulationHDF5Handler',
                 'ProjectHDF5Handler = pymontecarlo.formats.hdf5.project:ProjectHDF5Handler',

                 'XrayLineHDF5Handler = pymontecarlo.formats.hdf5.util.xrayline:XrayLineHDF5Handler',

                 'Options = pymontecarlo.formats.hdf5.options.options:OptionsHDF5Handler',

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

                 'ShowersLimitHDF5Handler = pymontecarlo.formats.hdf5.options.limit.showers:ShowersLimitHDF5Handler',
                 'UncertaintyLimitHDF5Handler = pymontecarlo.formats.hdf5.options.limit.uncertainty:UncertaintyLimitHDF5Handler',

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
                 'GeneratedPhotonIntensityResultResultHDF5Handler = pymontecarlo.formats.hdf5.results.photonintensity:GeneratedPhotonIntensityResultResultHDF5Handler',
                 'KRatioResultHDF5Handler = pymontecarlo.formats.hdf5.results.kratio:KRatioResultHDF5Handler',
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

