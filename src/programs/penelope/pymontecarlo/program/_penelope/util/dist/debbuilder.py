#!/usr/bin/env python
"""
================================================================================
:mod:`builder` -- Casino2 debian builder
================================================================================

.. module:: builder
   :synopsis: Casino2 debian builder

.. inheritance-diagram:: pymontecarlo.program.casino2.util.dist.deb.builder

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
from datetime import datetime
import shutil
import subprocess

# Third party modules.

# Local modules.
from pymontecarlo.util.dist.debbuilder import _DebBuilder

# Globals and constants variables.

class _PenelopeDebBuilder(_DebBuilder):

    def __init__(self, zip_path, package, fullname,
                 maintainer='Francesc Salvat <cesc@ecm.ub.es>',
                 authors=['Francesc Salvat', 'Jose M. Fernandez-Varea', 'Josep Sempau'],
                 section='science',
                 short_description='Code system for Monte Carlo simulation of electron and photon transport',
                 long_description='The computer code system PENELOPE performs Monte Carlo simulation of coupled electron-photon transport in arbitrary materials for a wide energy range, from a few hundred eV to about 1GeV. Photon transport is simulated by means of the standard, detailed simulation scheme. Electron and positron histories are generated on the basis of a mixed procedure, which combines detailed simulation of hard events with condensed simulation of soft interactions. A geometry package called PENGEOM permits the generation of random electron-photon showers in material systems consisting of homogeneous bodies limited by quadric surfaces, i.e. planes, spheres, cylinders, etc.\nThe report / proceedings are intended not only to serve as a manual of the PENELOPE code system, but also to provide the user with the necessary information to understand the details of the Monte Carlo algorithm.',
                 license='Distributed in agreement with OECD Nuclear Energy Agency. Permission to use, copy, modify, distribute and sell this software and its documentation for any purpose is hereby granted without fee, provided that the above copyright notice appears in all copies and that both that copyright notice and this permission notice appear in all supporting documentation. The Universitat de Barcelona makes no representations about the suitability of this software for any purpose. It is provided "as is" without express or implied warranty.',
                 homepage='https://www.oecd-nea.org/dbprog/courses/peneloperef.html',
                 priority='standard', depends=None, recommends=None):
        self._zip_path = zip_path

        version = os.path.splitext(os.path.basename(zip_path))[0].split('-')[1]
        date = datetime.fromtimestamp(os.path.getmtime(zip_path))

        _DebBuilder.__init__(self, package, fullname, version, maintainer,
                             authors, section, short_description,
                             long_description, date, license, homepage,
                             priority, depends, recommends)

class _PenelopeProgramDebBuilder(_PenelopeDebBuilder):

    def _compile(self, temp_dir, filepath, *args, **kwargs):
        dirname, filename = os.path.split(filepath)

        args = ['gfortran', '-Os', '-Wall', '-s']
        if kwargs['arch'] == 'i386':
            args.append('-m32')
        outfilename = os.path.splitext(filename)[0]
        args.append('-o%s' % outfilename)
        args.append(filename)

        subprocess.check_call(args, cwd=dirname)

        return os.path.join(dirname, outfilename)

    def _create_control(self, temp_dir, *args, **kwargs):
        control = _PenelopeDebBuilder._create_control(self, temp_dir, *args, **kwargs)
        control['Architecture'] = kwargs['arch']
        return control

    def build(self, outputdir, *args, **kwargs):
        if 'arch' not in kwargs:
            raise ValueError('Plese specify the architecture: amd64 or i386')
        _PenelopeDebBuilder.build(self, outputdir, *args, **kwargs)

class PenelopePendbaseDebBuilder(_PenelopeDebBuilder):

    def __init__(self, zip_path):
        _PenelopeDebBuilder.__init__(self, zip_path,
                                     package='penelope-pendbase',
                                     fullname='PENELOPE physics database',
                                     short_description="Tables of physical properties for PENELOPE",
                                     long_description="These data are extracted from the database, which consists of the 995 ASCII files. A material is completely characterized by its chemical composition, i.e., elements present and number of atoms of each element in a molecule (=stoichiometric index), mass density and mean excitation energy. Alloys and mixtures are treated as compounds, with stoichiometric indexes equal or proportional to the percent number of atoms of each element. Information about the material is supplied by the user from the keyboard, following the prompts from 'material', or read from the 'pdcompos.p08' file, which contains information for 280 different materials. In the case of compounds, 'molecular' cross sections are obtained by means of the additivity rule, i.e. as the sum of the atomic cross sections.")

    def _extract_zip(self, temp_dir, *args, **kwargs):
        with zipfile.ZipFile(self._zip_path, 'r') as z:
            for filename in z.namelist():
                if not filename.startswith('penelope/pendbase/pdfiles'):
                    continue
                z.extract(filename, temp_dir)

    def _create_folder_structure(self, temp_dir, *args, **kwargs):
        os.makedirs(os.path.join(temp_dir, 'DEBIAN'))
        os.makedirs(os.path.join(temp_dir, 'usr', 'share', self._package))
        os.makedirs(os.path.join(temp_dir, 'usr', 'share', 'doc', self._package))

    def _reorganize_files(self, temp_dir, *args, **kwargs):
        src_dir = os.path.join(temp_dir, 'penelope', 'pendbase', 'pdfiles')
        dst_dir = os.path.join(temp_dir, 'usr', 'share', self._package)
        shutil.move(src_dir, dst_dir)
        shutil.rmtree(os.path.join(temp_dir, 'penelope'))
#
    def _build(self, temp_dir, *args, **kwargs):
        self._extract_zip(temp_dir, *args, **kwargs)

        self._create_folder_structure(temp_dir, *args, **kwargs)

        self._reorganize_files(temp_dir, *args, **kwargs)

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

class PenelopeMaterialDebBuilder(_PenelopeProgramDebBuilder):

    def __init__(self, zip_path):
        _PenelopeProgramDebBuilder.__init__(self, zip_path,
                                            package='penelope-material',
                                            fullname='PENELOPE material program',
                                            short_description='Generates material definition files for PENELOPE',
                                            depends=['penelope-pendbase', 'libc6'])

    def _extract_zip(self, temp_dir, *args, **kwargs):
        with zipfile.ZipFile(self._zip_path, 'r') as z:
            for filename in z.namelist():
                if filename.startswith('penelope/fsource') or \
                        filename == 'penelope/pendbase/material-list.txt':
                    z.extract(filename, temp_dir)

    def _create_folder_structure(self, temp_dir, *args, **kwargs):
        _PenelopeProgramDebBuilder._create_folder_structure(self, temp_dir, *args, **kwargs)
        os.makedirs(os.path.join(temp_dir, 'usr', 'lib', self._package))

    def _compile_material(self, temp_dir, *args, **kwargs):
        filepath = os.path.join(temp_dir, 'penelope', 'fsource', 'material.f')
        outfilepath = self._compile(temp_dir, filepath, *args, **kwargs)

        dst = os.path.join(temp_dir, 'usr', 'lib', self._package)
        shutil.copy(outfilepath, dst)\

    def _reorganize_files(self, temp_dir, *args, **kwargs):
        src = os.path.join(temp_dir, 'penelope', 'pendbase', 'material-list.txt')
        dst = os.path.join(temp_dir, 'usr', 'share', self._package)
        shutil.move(src, dst)

        shutil.rmtree(os.path.join(temp_dir, 'penelope'))

    def _create_executable(self, temp_dir, *args, **kwargs):
        lines = []
        lines.append('#!/bin/sh')
        lines.append('cd /usr/share/penelope-pendbase')
        lines.append('/usr/lib/%s/material $@' % self._package)
        return lines

    def _write_executable(self, lines, temp_dir, *args, **kwargs):
        filepath = os.path.join(temp_dir, 'usr', 'bin', 'material')
        with open(filepath, 'w') as fp:
            fp.write('\n'.join(lines))
        os.chmod(filepath, 0o555)

    def _build(self, temp_dir, *args, **kwargs):
        self._extract_zip(temp_dir, *args, **kwargs)

        self._create_folder_structure(temp_dir, *args, **kwargs)

        self._compile_material(temp_dir, *args, **kwargs)

        self._reorganize_files(temp_dir, *args, **kwargs)

        lines = self._create_executable(temp_dir, *args, **kwargs)
        self._write_executable(lines, temp_dir, *args, **kwargs)

        manpage = self._create_man_page(temp_dir, 'material',
                                        synopsis='.B material\n[ < inputfile ]',
                                        *args, **kwargs)
        self._write_man_page(manpage, temp_dir, *args, **kwargs)

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
