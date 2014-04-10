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
from pymontecarlo.util.dist.debbuilder import \
    _DebBuilder, extract_exe_info, ManPage, DesktopEntry

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
            self.exe_info = extract_exe_info(temp_file.name)
        finally:
            os.remove(temp_file.name)

        _DebBuilder.__init__(self,
                             package='monaco',
                             fullname='MONACO',
                             version=self.exe_info['File version'], # dummy
                             maintainer='Silvia Richter <richter@gfe.rwth-aachen.de>',
                             authors=['P. Karduck', 'R. Amman', 'S. Richter', 'and collaborators'],
                             section='science',
                             short_description='Monte Carlo simulation of electron trajectory in solid',
                             long_description='Monte Carlo simulation software package developed at the Gemeinschaftslabor fuer Elektronenmikroskopie, RWTH Aachen University',
                             date=datetime.strptime(self.exe_info['Link date'], '%I:%M %p %d/%m/%Y'), # dummy
                             license='Freeware',
                             homepage='http://www.gfe.rwth-aachen.de',
                             depends=['wine'])

    def _extract_zip(self, temp_dir, *args, **kwargs):
        with zipfile.ZipFile(self._zip_path, 'r') as z:
            z.extractall(temp_dir)

    def _organize_files(self, temp_dir, *args, **kwargs):
        # Copy files to share
        src_dir = os.path.join(temp_dir, 'monaco')
        dst = os.path.join(temp_dir, 'usr', 'share', self.package)
        for filename in os.listdir(src_dir):
            shutil.move(os.path.join(src_dir, filename), dst)
        os.remove(os.path.join(dst, 'Mcconv.exe'))

        # Copy icon
        dst_dir = os.path.join(temp_dir, 'usr', 'share', 'icons',
                               'hicolor', '48x48', 'apps')
        os.makedirs(dst_dir, exist_ok=True)

        src = os.path.join(os.path.dirname(self._zip_path), 'monaco.png')
        dst = os.path.join(dst_dir, 'monaco.png')
        shutil.copy(src, dst)

        # Remove temporary directory
        shutil.rmtree(src_dir)

    def _create_mccli(self, temp_dir, *args, **kwargs):
        lines = []
        lines.append('#!/bin/sh')
        lines.append('cd /usr/share/%s' % self.package)
        lines.append('wine /usr/share/%s/Mccli32.exe $@' % self.package)

        appname = 'mccli'
        short_description = 'Command line interface to the MONACO software package'

        manpage = ManPage(package=self.package,
                          name=appname,
                          short_description=short_description,
                          synopsis='.B %s {\n.I help, int, phi, dwdrz, sim, test, comp\n.B } [\n.I options\n.B ]' % appname,
                          see_also=self.homepage)

        return lines, manpage, None

    def _create_mccorr(self, temp_dir, *args, **kwargs):
        lines = []
        lines.append('#!/bin/sh')
        lines.append('cd /usr/share/%s' % self.package)
        lines.append('wine /usr/share/%s/Mccorr32.exe' % self.package)

        appname = 'mccorr'
        short_description = 'Analyze, process and extract data from simulations'

        manpage = ManPage(package=self.package,
                          name=appname,
                          short_description=short_description,
                          synopsis='.B %s' % appname,
                          see_also=self.homepage)

        entry = DesktopEntry(type_=DesktopEntry.TYPE_APPLICATION,
                             name="MC Corr",
                             genericname=short_description,
                             nodisplay=False,
                             icon='monaco',
                             exec_=appname,
                             terminal=False,
                             categories=['Science'])

        return lines, manpage, entry

    def _create_mcdemo(self, temp_dir, *args, **kwargs):
        lines = []
        lines.append('#!/bin/sh')
        lines.append('cd /usr/share/%s' % self.package)
        lines.append('wine /usr/share/%s/Mcdemo32.exe' % self.package)

        appname = 'mcdemo'
        short_description = 'Demonstration program for tracking the electron trajectories'

        manpage = ManPage(package=self.package,
                          name=appname,
                          short_description=short_description,
                          synopsis='.B %s' % appname,
                          see_also=self.homepage)

        entry = DesktopEntry(type_=DesktopEntry.TYPE_APPLICATION,
                             name="MC Demo",
                             genericname=short_description,
                             nodisplay=False,
                             icon='monaco',
                             exec_=appname,
                             terminal=False,
                             categories=['Science'])

        return lines, manpage, entry

    def _create_mclib(self, temp_dir, *args, **kwargs):
        lines = []
        lines.append('#!/bin/sh')
        lines.append('cd /usr/share/%s' % self.package)
        lines.append('wine /usr/share/%s/Mclib32.exe' % self.package)

        appname = 'mclib'
        short_description = 'Setup material parameters to create simulation'

        manpage = ManPage(package=self.package,
                          name=appname,
                          short_description=short_description,
                          synopsis='.B %s' % appname,
                          see_also=self.homepage)

        entry = DesktopEntry(type_=DesktopEntry.TYPE_APPLICATION,
                             name="MC Demo",
                             genericname=short_description,
                             nodisplay=False,
                             icon='monaco',
                             exec_=appname,
                             terminal=False,
                             categories=['Science'])

        return lines, manpage, entry

    def _create_mcpack(self, temp_dir, *args, **kwargs):
        lines = []
        lines.append('#!/bin/sh')
        lines.append('cd /usr/share/%s' % self.package)
        lines.append('wine /usr/share/%s/Mcpack32.exe' % self.package)

        appname = 'mcpack'
        short_description = 'Control program to start individual applications'

        manpage = ManPage(package=self.package,
                          name=appname,
                          short_description=short_description,
                          synopsis='.B %s' % appname,
                          see_also=self.homepage)

        entry = DesktopEntry(type_=DesktopEntry.TYPE_APPLICATION,
                             name="MC Pack",
                             genericname=short_description,
                             nodisplay=False,
                             icon='monaco',
                             exec_=appname,
                             terminal=False,
                             categories=['Science'])

        return lines, manpage, entry

    def _create_mcsim(self, temp_dir, *args, **kwargs):
        lines = []
        lines.append('#!/bin/sh')
        lines.append('cd /usr/share/%s' % self.package)
        lines.append('wine /usr/share/%s/Mcsim32.exe' % self.package)

        appname = 'mcsim'
        short_description = 'Run simulations added to the batch'

        manpage = ManPage(package=self.package,
                          name=appname,
                          short_description=short_description,
                          synopsis='.B %s' % appname,
                          see_also=self.homepage)

        entry = DesktopEntry(type_=DesktopEntry.TYPE_APPLICATION,
                             name="MC Sim",
                             genericname=short_description,
                             nodisplay=False,
                             icon='monaco',
                             exec_=appname,
                             terminal=False,
                             categories=['Science'])

        return lines, manpage, entry

    def _write_executable(self, lines, manpage, entry, temp_dir, *args, **kwargs):
        os.makedirs(os.path.join(temp_dir, 'usr', 'bin'), exist_ok=True)
        filepath = os.path.join(temp_dir, 'usr', 'bin', manpage.name)
        with open(filepath, 'w') as fp:
            fp.write('\n'.join(lines))
        os.chmod(filepath, 0o555)

        if manpage is not None:
            self._write_man_page(manpage, temp_dir, *args, **kwargs)
        if entry is not None:
            self._write_desktop_entry(entry, temp_dir, *args, **kwargs)

    def _build(self, temp_dir, *args, **kwargs):
        self._extract_zip(temp_dir, *args, **kwargs)

        self._organize_files(temp_dir, *args, **kwargs)

        lines, manpage, entry = self._create_mccli(temp_dir, *args, **kwargs)
        self._write_executable(lines, manpage, entry, temp_dir, *args, **kwargs)

        lines, manpage, entry = self._create_mccorr(temp_dir, *args, **kwargs)
        self._write_executable(lines, manpage, entry, temp_dir, *args, **kwargs)

        lines, manpage, entry = self._create_mcdemo(temp_dir, *args, **kwargs)
        self._write_executable(lines, manpage, entry, temp_dir, *args, **kwargs)

        lines, manpage, entry = self._create_mclib(temp_dir, *args, **kwargs)
        self._write_executable(lines, manpage, entry, temp_dir, *args, **kwargs)

        lines, manpage, entry = self._create_mcpack(temp_dir, *args, **kwargs)
        self._write_executable(lines, manpage, entry, temp_dir, *args, **kwargs)

        lines, manpage, entry = self._create_mcsim(temp_dir, *args, **kwargs)
        self._write_executable(lines, manpage, entry, temp_dir, *args, **kwargs)

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

        lines = self._create_copyright(temp_dir, *args, **kwargs)
        self._write_copyright(lines, temp_dir, *args, **kwargs)

        changelog = self._create_changelog(temp_dir, *args, **kwargs)
        self._write_changelog(changelog, temp_dir, *args, **kwargs)


