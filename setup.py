#!/usr/bin/env python

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import re
from ConfigParser import SafeConfigParser

# Third party modules.
from cx_Freeze import setup, Executable

# Local modules.
from pymontecarlo import find_programs, load_program, get_program_setup

# Globals and constants variables.

# Collect options
packages = ['pymontecarlo',
            'pymontecarlo.input',
            'pymontecarlo.io',
            'pymontecarlo.output',
            'pymontecarlo.program',
            'pymontecarlo.runner',
            'pymontecarlo.ui',
            'pymontecarlo.ui.cli',
            'pymontecarlo.util']
py_modules = []
package_dir = {'pymontecarlo': 'code/pymontecarlo'}
package_data = {'pymontecarlo.util': ['data/*']}
ext_modules = []
cmdclass = {}

# Find programs to build
config = SafeConfigParser()
with open('setup.cfg', 'r') as fp:
    config.readfp(fp)
try:
    programs = config.get('pymontecarlo', 'programs').strip()
    if not programs:
        programs = find_programs()
    else:
        programs = re.findall(r'[^,;\s]+', programs)
except:
    programs = find_programs()

print 'Building programs: %s' % ', '.join(programs)

# Collect options for all programs
for name in programs:
    program = load_program(name, validate=False)
    setupcfg = get_program_setup(program)

    packages += setupcfg.packages
    py_modules += setupcfg.py_modules
    package_dir.update(setupcfg.package_dir)
    package_data.update(setupcfg.package_data)
    ext_modules += setupcfg.ext_modules
    cmdclass.update(setupcfg.cmdclass)

# cx_freeze options
excludes = ['Tkinter']
includes = ['encodings.ascii', 'site']

build_exe_options = \
    {"create_shared_zip": True,
     "compressed": True,
     "optimize": 2,
     'packages': packages,
     'includes': includes,
     'excludes': excludes}

# cx_freeze executables
cli_main_exec = \
    Executable("code/pymontecarlo/ui/cli/main.py")
cli_configure_exec = \
    Executable("code/pymontecarlo/ui/cli/configure.py")

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
      py_modules=py_modules,
      package_dir=package_dir,
      package_data=package_data,

      ext_modules=ext_modules,
      cmdclass=cmdclass,

      options={"build_exe": build_exe_options},
      executables=[cli_main_exec, cli_configure_exec]
)

