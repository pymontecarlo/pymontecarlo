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
import glob

# Third party modules.

# Local modules.
from pymontecarlo.util.dist.debbuilder import \
    _DebBuilder, extract_exe_info, ManPage, DesktopEntry

# Globals and constants variables.

class MCXrayDebBuilder(_DebBuilder):

    def __init__(self, zip_path):
        self._zip_path = zip_path

        # Exe info
        temp_file = tempfile.NamedTemporaryFile(suffix='.exe', delete=False)
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                for filename in z.namelist():
                    if filename.endswith('McXRayLite.exe'):
                        break
                temp_file.write(z.read(filename))
                temp_file.close()
            self.exe_info = extract_exe_info(temp_file.name)
        finally:
            os.remove(temp_file.name)

        _DebBuilder.__init__(self,
                             package='mcxray-lite',
                             fullname='MCX-Ray Lite',
                             version=self.exe_info['File version'], # dummy
                             maintainer='Raynald Gauvin <raynald.gauvin@mcgill.ca>',
                             authors=['Raynald Gauvin', 'Pierre Michaud', 'Hendrix Demers'],
                             section='science',
                             short_description='Monte Carlo simulation of electron trajectory in solid',
                             long_description='MC X-Ray is a new Monte Carlo program that is an extension of the Monte Carlo programs Casino and Win X-Ray since it computes the complete x-ray spectra from the simulation of electron scattering in solids of various types of geometries. MC X-Ray allows up to 256 different regions in the materials having shape of spheres, cylinders and combinations of horizontal and vertical planes. All these regions can have a different composition. This program was written by Pierre Michaud under the supervision of Pr. Gauvin. Dr. Hendrix Demers improved and validated the x-ray spectrum computation of MC X-Ray.',
                             date=datetime.strptime(self.exe_info['Link date'], '%I:%M %p %d/%m/%Y'), # dummy
                             license='Private',
                             homepage='http://montecarlomodeling.mcgill.ca/software/mcxray/mcxray.html',
                             depends=['wine'])

    def _extract_zip(self, temp_dir, *args, **kwargs):
        dirpath = os.path.join(temp_dir, 'zip')
        os.makedirs(dirpath)
        with zipfile.ZipFile(self._zip_path, 'r') as z:
            for filename in z.namelist(): # Cannot use extract all, problem in zip
                z.extract(filename, dirpath)

    def _organize_files(self, temp_dir, *args, **kwargs):
        # Copy zip content in share
        dst = os.path.join(temp_dir, 'usr', 'share', self.package)
        os.makedirs(dst, exist_ok=True)

        src_dir = os.path.join(temp_dir, 'zip')
        for filename in os.listdir(src_dir):
            shutil.move(os.path.join(src_dir, filename), dst)

        # Move documentation
        dst = os.path.join(temp_dir, 'usr', 'share', 'doc', self.package)
        os.makedirs(dst, exist_ok=True)

        for src in glob.iglob(os.path.join(temp_dir, 'usr', 'share',
                                           self.package, 'Documentations', '*')):
            shutil.copy(src, dst)
        shutil.rmtree(os.path.join(temp_dir, 'usr', 'share',
                                   self.package, 'Documentations'))

        # Remove other architecture exe
        arch = kwargs['arch']
        if arch == 'amd64':
            os.remove(os.path.join(temp_dir, 'usr', 'share',
                                   self.package, 'McXRayLite.exe'))
        elif arch == 'i386':
            os.remove(os.path.join(temp_dir, 'usr', 'share',
                                   self.package, 'McXRayLite_x64.exe'))

        shutil.rmtree(src_dir)

    def _create_executable(self, temp_dir, *args, **kwargs):
        arch = kwargs['arch']
        if arch == 'amd64':
            filename = 'McXRayLite_x64.exe'
        elif arch == 'i386':
            filename = 'McXRayLite.exe'

        lines = []
        lines.append('#!/bin/sh')
        lines.append('cd /usr/share/%s' % self.package)
        lines.append('wine /usr/share/%s/%s $@' % (self.package, filename))
        return lines

    def _write_executable(self, lines, temp_dir, *args, **kwargs):
        os.makedirs(os.path.join(temp_dir, 'usr', 'bin'), exist_ok=True)
        filepath = os.path.join(temp_dir, 'usr', 'bin', 'mcxray')
        with open(filepath, 'w') as fp:
            fp.write('\n'.join(lines))
        os.chmod(filepath, 0o555)

    def _create_man_page(self, temp_dir, *args, **kwargs):
        return ManPage(package=self.package,
                       name='mcxray',
                       short_description=self.short_description,
                       synopsis='.B mcxray',
                       long_description=self.long_description,
                       see_also=self.homepage)

    def _create_desktop_entry(self, temp_dir, *args, **kwargs):
        return DesktopEntry(type_=DesktopEntry.TYPE_APPLICATION,
                            name=self.fullname,
                            genericname=self.short_description,
                            nodisplay=False,
                            icon='mcxray',
                            exec_='mcxray',
                            terminal=False,
                            categories=['Science'])

    def _write_desktop_entry(self, entry, temp_dir, *args, **kwargs):
        _DebBuilder._write_desktop_entry(self, entry, temp_dir, *args, **kwargs)

        # Copy icon
        dst_dir = os.path.join(temp_dir, 'usr', 'share', 'icons',
                               'hicolor', '48x48', 'apps')
        os.makedirs(dst_dir, exist_ok=True)

        src = os.path.join(os.path.dirname(self._zip_path), 'McXRayLite.png')
        dst = os.path.join(dst_dir, 'mcxray.png')
        shutil.copy(src, dst)

    def _create_control(self, temp_dir, *args, **kwargs):
        control = _DebBuilder._create_control(self, temp_dir, *args, **kwargs)
        control['Architecture'] = kwargs['arch']
        return control

    def _build(self, temp_dir, *args, **kwargs):
        self._extract_zip(temp_dir, *args, **kwargs)

        self._organize_files(temp_dir, *args, **kwargs)

        lines = self._create_executable(temp_dir, *args, **kwargs)
        self._write_executable(lines, temp_dir, *args, **kwargs)

        manpage = self._create_man_page(temp_dir, *args, **kwargs)
        self._write_man_page(manpage, temp_dir, *args, **kwargs)

        entry = self._create_desktop_entry(temp_dir, *args, **kwargs)
        self._write_desktop_entry(entry, temp_dir, *args, **kwargs)

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

    def build(self, outputdir, *args, **kwargs):
        if 'arch' not in kwargs:
            raise ValueError('Plese specify the architecture: amd64 or i386')
        _DebBuilder.build(self, outputdir, *args, **kwargs)
