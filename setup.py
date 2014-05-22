#!/usr/bin/env python

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import sys
import codecs
import re
import platform
from distutils.core import Command
from distutils.dir_util import remove_tree, copy_tree
from distutils.file_util import copy_file
from distutils.archive_util import make_archive
from distutils import log

# Third party modules.
from setuptools import setup, find_packages
import pkg_resources

try:
    from cx_Freeze.dist import Distribution, build, build_exe as _build_exe
    from cx_Freeze.freezer import Executable
    from cx_Freeze.macdist import \
        bdist_mac as _bdist_mac, bdist_dmg as _bdist_dmg
    has_cx_freeze = True
except ImportError:
    has_cx_freeze = False

# Local modules.
from pymontecarlo.util.dist.command import clean as _clean

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

class clean(_clean):

    user_options = _clean.user_options + \
        [('build-exe=', 'b',
         'directory for built executables'), ]

    def initialize_options(self):
        _clean.initialize_options(self)
        self.build_exe = None

    def finalize_options(self):
        _clean.finalize_options(self)
        self.set_undefined_options('build_exe',
                                   ('build_exe', 'build_exe'))

    def run(self):
        if self.all:
            # remove build directories
            for directory in (self.build_exe,):
                if os.path.exists(directory):
                    remove_tree(directory, dry_run=self.dry_run)
                else:
                    log.warn("'%s' does not exist -- can't clean it",
                             directory)

        _clean.run(self)

if has_cx_freeze:
    class build_exe(_build_exe):

        def run(self):
            _build_exe.run(self)

            # Add egg info of dependencies
            for dist in pkg_resources.require('pymontecarlo'):
                egg_info_dirpath = dist._provider.egg_info or dist._provider.path
                if egg_info_dirpath is None:
                    log.warn('No egg-info found for project %s' % dist.project_name)
                    continue

                if os.path.isdir(egg_info_dirpath):
                    if os.path.basename(egg_info_dirpath) == 'EGG-INFO':
                        dst = os.path.join(self.build_exe, dist.egg_name() + '.egg-info')
                    else:
                        dst = os.path.join(self.build_exe,
                                           os.path.basename(egg_info_dirpath))
                    copy_tree(egg_info_dirpath, dst)
                else:
                    copy_file(egg_info_dirpath, self.build_exe)

    class bdist_mac(_bdist_mac):

        user_options = _bdist_mac.user_options + \
            [('dist-dir=', 'd',
              "directory to put final built distributions in "
              "[default: dist]"), ]

        def initialize_options(self):
            _bdist_mac.initialize_options(self)
            self.dist_dir = None

        def finalize_options(self):
            _bdist_mac.finalize_options(self)

            if self.dist_dir is None:
                self.dist_dir = "dist"

        def run(self):
            # Modify to run on all executables
            for executable in list(self.distribution.executables):
                self.distribution.executables.remove(executable)
                self.distribution.executables.insert(0, executable)

                _bdist_mac.run(self)

                copy_tree(self.bundleDir,
                          os.path.join(self.dist_dir, executable.shortcutName + '.app'))

    class bdist_dmg(_bdist_dmg):

        user_options = _bdist_dmg.user_options + \
            [('dist-dir=', 'd',
              "directory to put final built distributions in "
              "[default: dist]"), ]

        def initialize_options(self):
            _bdist_dmg.initialize_options(self)
            self.dist_dir = None

        def finalize_options(self):
            _bdist_dmg.finalize_options(self)

            if self.dist_dir is None:
                self.dist_dir = "dist"

        def buildDMG(self):
            for executable in list(self.distribution.executables):
                self.volume_label = 'pymontecarlo-%s.dmg' % executable.shortcutName
                self.dmgName = os.path.join(self.dist_dir, self.volume_label)
                self.bundleDir = os.path.join(self.dist_dir,
                                              executable.shortcutName + '.app')
                _bdist_dmg.buildDMG(self)

    class bdist_exe(Command):

        user_options = _bdist_dmg.user_options + \
            [('dist-dir=', 'd',
              "directory to put final built distributions in "
              "[default: dist]"), ]

        def initialize_options(self):
            self.dist_dir = None

        def finalize_options(self):
            if self.dist_dir is None:
                self.dist_dir = "dist"

        def run(self):
            self.run_command('build_exe')

            build_dir = self.get_finalized_command("build_exe").build_exe
            base_name = os.path.join(self.dist_dir,
                                     "pymontecarlo-%s" % platform.machine())
            make_archive(base_name, 'zip', build_dir)

packages = find_packages(exclude=('pymontecarlo.util.dist*',))
namespace_packages = ['pymontecarlo',
                      'pymontecarlo.program']
requirements = ['pyparsing', 'numpy', 'h5py', 'matplotlib', 'PySide',
                'pyxray', 'Pillow']

excludes = ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'pywin.debugger',
            'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
            'Tkconstants', 'tkinter', "wx", "scipy", "PyQt4",
            'ConfigParser', 'IPython', 'pygments', 'sphinx',
            'pyxray' # Because data files from pyxray are not copied in zip
            ]
includes = ['PIL' # Requires by some programs
            ]

build_exe_options = {"packages": packages,
                     "namespace_packages": namespace_packages,
                     "excludes": excludes,
                     "includes": includes,
                     "init_script": os.path.abspath('initscripts/Console.py'),
                     'include_msvcr': True}

cli_executables = {'pymontecarlo-configure': 'pymontecarlo.ui.cli.configure:run',
                   'pymontecarlo-cli': 'pymontecarlo.ui.cli.main:run',
                   'pymontecarlo-updater': 'pymontecarlo.ui.cli.updater:run'}
gui_executables = {'pymontecarlo': 'pymontecarlo.ui.gui.main:run'}

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
                     'PhotonPolarAngularDetector = pymontecarlo.fileformat.options.detector:PhotonPolarAngularDetectorXMLHandler',
                     'PhotonAzimuthalAngularDetector = pymontecarlo.fileformat.options.detector:PhotonAzimuthalAngularDetectorXMLHandler',
                     'EnergyDepositedSpatialDetector = pymontecarlo.fileformat.options.detector:EnergyDepositedSpatialDetectorXMLHandler',
                     'PhotonSpectrumDetector = pymontecarlo.fileformat.options.detector:PhotonSpectrumDetectorXMLHandler',
                     'PhotonDepthDetector = pymontecarlo.fileformat.options.detector:PhotonDepthDetectorXMLHandler',
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
                     'PhotonRadialResult = pymontecarlo.fileformat.results.result:PhotonRadialResultHDF5Handler',
                     'TimeResult = pymontecarlo.fileformat.results.result:TimeResultHDF5Handler',
                     'ShowersStatisticsResult = pymontecarlo.fileformat.results.result:ShowersStatisticsResultHDF5Handler',
                     'ElectronFractionResult = pymontecarlo.fileformat.results.result:ElectronFractionResultHDF5Handler',
                     'TrajectoryResult = pymontecarlo.fileformat.results.result:TrajectoryResultHDF5Handler',
                     'BackscatteredElectronEnergyResult = pymontecarlo.fileformat.results.result:BackscatteredElectronEnergyResultHDF5Handler',
                     'TransmittedElectronEnergyResult = pymontecarlo.fileformat.results.result:TransmittedElectronEnergyResultHDF5Handler',
                     'BackscatteredElectronPolarAngularResult = pymontecarlo.fileformat.results.result:BackscatteredElectronPolarAngularResultHDF5Handler',
                     'BackscatteredElectronRadialResult = pymontecarlo.fileformat.results.result:BackscatteredElectronRadialResultHDF5Handler', ],

                'pymontecarlo.ui.gui.options.beam':
                    ['PencilBeam = pymontecarlo.ui.gui.options.beam:PencilBeamWidget',
                     'GaussianBeam = pymontecarlo.ui.gui.options.beam:GaussianBeamWidget', ],
                'pymontecarlo.ui.gui.options.material':
                    ['Material = pymontecarlo.ui.gui.options.material:MaterialDialog'],
                'pymontecarlo.ui.gui.options.geometry':
                    ['Substrate = pymontecarlo.ui.gui.options.geometry:SubstrateWidget',
                     'Inclusion = pymontecarlo.ui.gui.options.geometry:InclusionWidget',
                     'HorizontalLayers = pymontecarlo.ui.gui.options.geometry:HorizontalLayersWidget',
                     'VerticalLayers = pymontecarlo.ui.gui.options.geometry:VerticalLayersWidget',
                     'Sphere = pymontecarlo.ui.gui.options.geometry:SphereWidget'],
                'pymontecarlo.ui.gui.options.detector':
                    ['BackscatteredElectronEnergyDetector = pymontecarlo.ui.gui.options.detector:BackscatteredElectronEnergyDetectorWidget',
                     'TransmittedElectronEnergyDetector = pymontecarlo.ui.gui.options.detector:TransmittedElectronEnergyDetectorWidget',
                     'BackscatteredElectronPolarAngularDetector = pymontecarlo.ui.gui.options.detector:BackscatteredElectronPolarAngularDetectorWidget',
                     'TransmittedElectronPolarAngularDetector = pymontecarlo.ui.gui.options.detector:TransmittedElectronPolarAngularDetectorWidget',
                     'BackscatteredElectronAzimuthalAngularDetector = pymontecarlo.ui.gui.options.detector:BackscatteredElectronAzimuthalAngularDetectorWidget',
                     'TransmittedElectronAzimuthalAngularDetector = pymontecarlo.ui.gui.options.detector:TransmittedElectronAzimuthalAngularDetectorWidget',
                     'BackscatteredElectronRadialDetector = pymontecarlo.ui.gui.options.detector:BackscatteredElectronRadialDetectorWidget',
                     'PhotonPolarAngularDetector = pymontecarlo.ui.gui.options.detector:PhotonPolarAngularDetectorWidget',
                     'PhotonAzimuthalAngularDetector = pymontecarlo.ui.gui.options.detector:PhotonAzimuthalAngularDetectorWidget',
#                     'EnergyDepositedSpatialDetector = pymontecarlo.ui.gui.options.detector:EnergyDepositedSpatialDetectorWidget',
                     'PhotonSpectrumDetector = pymontecarlo.ui.gui.options.detector:PhotonSpectrumDetectorWidget',
                     'PhotonDepthDetector = pymontecarlo.ui.gui.options.detector:PhotonDepthDetectorWidget',
                     'PhotonRadialDetector = pymontecarlo.ui.gui.options.detector:PhotonRadialDetectorWidget',
                     'PhotonEmissionMapDetector = pymontecarlo.ui.gui.options.detector:PhotonEmissionMapDetectorWidget',
                     'PhotonIntensityDetector = pymontecarlo.ui.gui.options.detector:PhotonIntensityDetectorWidget',
                     'TimeDetector = pymontecarlo.ui.gui.options.detector:TimeDetectorWidget',
                     'ElectronFractionDetector = pymontecarlo.ui.gui.options.detector:ElectronFractionDetectorWidget',
                     'ShowersStatisticsDetector = pymontecarlo.ui.gui.options.detector:ShowersStatisticsDetectorWidget',
                     'TrajectoryDetector = pymontecarlo.ui.gui.options.detector:TrajectoryDetectorWidget', ],
                'pymontecarlo.ui.gui.options.limit':
                    ['TimeLimit = pymontecarlo.ui.gui.options.limit:TimeLimitWidget',
                     'ShowersLimit = pymontecarlo.ui.gui.options.limit:ShowersLimitWidget',
#                     'UncertaintyLimit = pymontecarlo.ui.gui.options.limit:UncertaintyLimitWidget '
                    ],
                'pymontecarlo.ui.gui.results.result':
                    ['PhotonIntensityResult = pymontecarlo.ui.gui.results.result:PhotonIntensityResultWidget',
                     'PhotonSpectrumResult = pymontecarlo.ui.gui.results.result:PhotonSpectrumResultWidget',
                     'PhotonDepthResult = pymontecarlo.ui.gui.results.result:PhotonDepthResultWidget',
                     'PhotonRadialResult = pymontecarlo.ui.gui.results.result:PhotonRadialResultWidget',
                     'TimeResult = pymontecarlo.ui.gui.results.result:TimeResultWidget',
                     'ShowersStatisticsResult = pymontecarlo.ui.gui.results.result:ShowersStatisticsResultWidget',
                     'ElectronFractionResult = pymontecarlo.ui.gui.results.result:ElectronFractionResultWidget',
                     'TrajectoryResult = pymontecarlo.ui.gui.results.result:TrajectoryResultWidget',
                     'BackscatteredElectronEnergyResult = pymontecarlo.ui.gui.results.result:BackscatteredElectronEnergyResultWidget',
                     'TransmittedElectronEnergyResult = pymontecarlo.ui.gui.results.result:TransmittedElectronEnergyResultWidget',
                     'BackscatteredElectronPolarAngularResult = pymontecarlo.ui.gui.results.result:BackscatteredElectronPolarAngularResultWidget',
                     'BackscatteredElectronRadialResult = pymontecarlo.ui.gui.results.result:BackscatteredElectronRadialResultWidget', ],
                }


entry_points['console_scripts'] = \
    ['%s = %s' % item for item in cli_executables.items()]
entry_points['gui_scripts'] = \
    ['%s = %s' % item for item in gui_executables.items()]

if has_cx_freeze:
    def _make_executable(target_name, script, gui=False):
        path = os.path.join(*script.split(":")[0].split('.')) + '.py'
        if sys.platform == "win32": target_name += '.exe'
        base = "Win32GUI" if sys.platform == "win32" and gui else None
        return Executable(path, targetName=target_name, base=base,
                          shortcutName=target_name)

    executables = []
    for target_name, script in cli_executables.items():
        executables.append(_make_executable(target_name, script, False))
    for target_name, script in gui_executables.items():
        executables.append(_make_executable(target_name, script, True))

    distclass = Distribution
    cmdclass = {"build": build, "build_exe": build_exe, "bdist_exe": bdist_exe,
                "bdist_mac": bdist_mac, "bdist_dmg": bdist_dmg,
                'clean': clean}
else:
    executables = []
    distclass = None
    cmdclass = {'clean': clean}

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

      distclass=distclass,
      cmdclass=cmdclass,

      setup_requires=['nose'],
      install_requires=requirements,

      entry_points=entry_points,
      executables=executables,

      options={"build_exe": build_exe_options},

      test_suite='nose.collector',
)

