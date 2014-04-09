#!/usr/bin/env python
"""
================================================================================
:mod:`debbuilder` -- Monaco debian builder
================================================================================

.. module:: debbuilder
   :synopsis: Monaco debian builder

.. inheritance-diagram:: pymontecarlo.program.monaco.util.dist.debbuilder

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import zipfile
import tempfile
from datetime import datetime
import shutil

# Third party modules.

# Local modules.
from pymontecarlo.util.dist.debbuilder import _DebBuilder, extract_exe_info

# Globals and constants variables.

class MonacoDebBuilder(_DebBuilder):

    def __init__(self, zip_path):
        self._zip_path = zip_path

        # Exe info
        temp_file = tempfile.NamedTemporaryFile(suffix='.exe', delete=False)
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                for filename in z.namelist():
                    if filename.endswith('Mclib32.exe'):
                        break
                temp_file.write(z.read(filename))
                temp_file.close()
            self._exe_info = extract_exe_info(temp_file.name)
        finally:
            os.remove(temp_file.name)

        _DebBuilder.__init__(self,
                             package='monaco',
                             fullname='MONACO',
                             version=self._exe_info['File version'], # dummy
                             maintainer='Silvia Richter <richter@gfe.rwth-aachen.de>',
                             authors=['P. Karduck', 'R. Amman', 'S. Richter', 'and collaborators'],
                             section='science',
                             short_description='Monte Carlo simulation of electron trajectory in solid',
                             long_description='Monte Carlo simulation software package developed at the Gemeinschaftslabor fuer Elektronenmikroskopie, RWTH Aachen University',
                             date=datetime.strptime(self._exe_info['Link date'], '%I:%M %p %d/%m/%Y'), # dummy
                             license='Private',
                             homepage='http://www.gfe.rwth-aachen.de',
                             depends=['wine'])

    def _extract_zip(self, temp_dir, *args, **kwargs):
        with zipfile.ZipFile(self._zip_path, 'r') as z:
            z.extractall(temp_dir)

    def _reorganize_files(self, temp_dir, *args, **kwargs):
        def _find(name, path):
            for root, _dirs, files in os.walk(path):
                if name in files:
                    return os.path.join(root, name)

        src_dir = os.path.join(temp_dir, 'monaco')
        dst_dir = os.path.join(temp_dir, 'usr', 'share', self._package)
        for filename in os.listdir(src_dir):
            shutil.move(os.path.join(src_dir, filename), dst_dir)

        shutil.rmtree(src_dir)
        os.remove(os.path.join(dst_dir, 'Mcconv.exe'))

    def _create_executables(self, temp_dir, *args, **kwargs):
        filenames = ['Mccli32.exe', 'Mccorr32.exe', 'Mcdemo32.exe',
                     'Mclib32.exe', 'Mcpack32.exe', 'Mcsim32.exe']

        exe_lines = {}
        for filename in filenames:
            lines = []
            lines.append('#!/bin/sh')
            lines.append('cd /usr/share/%s' % self._package)
            lines.append('wine /usr/share/%s/%s $@' % (self._package, filename))
            exe_lines[filename] = lines

        return exe_lines

    def _write_executables(self, exe_lines, temp_dir, *args, **kwargs):
        for filename, lines in exe_lines.items():
            filename = filename.lower().rstrip('.exe')
            filepath = os.path.join(temp_dir, 'usr', 'bin', filename)
            with open(filepath, 'w') as fp:
                fp.write('\n'.join(lines))
            os.chmod(filepath, 0o555)

    def _build(self, temp_dir, *args, **kwargs):
        self._extract_zip(temp_dir, *args, **kwargs)

        self._create_folder_structure(temp_dir, *args, **kwargs)

        self._reorganize_files(temp_dir, *args, **kwargs)

        exe_lines = self._create_executables(temp_dir, *args, **kwargs)
        self._write_executables(exe_lines, temp_dir, *args, **kwargs)

        control = self._create_control(temp_dir, *args, **kwargs)
        self._write_control(control, temp_dir, *args, **kwargs)

        lines = self._create_preinst(temp_dir, *args, **kwargs)
        self._write_preinst(lines, temp_dir, *args, **kwargs)

        lines = self._create_postinst(temp_dir, *args, **kwargs)
        self._write_postinst(lines, temp_dir, *args, **kwargs)

        lines = self._create_prerm(temp_dir, *args, **kwargs)
        self._write_prerm(lines, temp_dir, *args, **kwargs)

        lines = self._create_postrm(temp_dir, *args, **kwargs)
        self._write_postrm(lines, temp_dir, *args, **kwargs)

        manpage = self._create_man_page(temp_dir, 'mccli32',
                                        short_description='Command line interface to the MONACO software package',
                                        long_description='',
                                        synopsis='.B mccli {\n.I help, int, phi, dwdrz, sim, test, comp\n.B } [\n.I options\n.B ]')
        self._write_man_page(manpage, temp_dir, *args, **kwargs)

        manpage = self._create_man_page(temp_dir, 'mcdemo32',
                                        short_description='Demonstration program for tracking the electron trajectories',
                                        long_description='')
        self._write_man_page(manpage, temp_dir, *args, **kwargs)

        manpage = self._create_man_page(temp_dir, 'mclib32',
                                        short_description='Setup material parameters to create simulation',
                                        long_description='')
        self._write_man_page(manpage, temp_dir, *args, **kwargs)

        manpage = self._create_man_page(temp_dir, 'mcsim32',
                                        short_description='Run simulations added to the batch',
                                        long_description='')
        self._write_man_page(manpage, temp_dir, *args, **kwargs)

        manpage = self._create_man_page(temp_dir, 'mccorr32',
                                        short_description='Analyze, process and extract data from simulations',
                                        long_description='')
        self._write_man_page(manpage, temp_dir, *args, **kwargs)

        manpage = self._create_man_page(temp_dir, 'mcpack32',
                                        short_description='Control program to start individual applications',
                                        long_description='')
        self._write_man_page(manpage, temp_dir, *args, **kwargs)

        lines = self._create_copyright(temp_dir, *args, **kwargs)
        self._write_copyright(lines, temp_dir, *args, **kwargs)

        changelog = self._create_changelog(temp_dir, *args, **kwargs)
        self._write_changelog(changelog, temp_dir, *args, **kwargs)


