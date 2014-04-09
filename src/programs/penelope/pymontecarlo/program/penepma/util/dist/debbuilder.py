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
import shutil
import glob

# Third party modules.

# Local modules.
from pymontecarlo.program._penelope.util.dist.debbuilder import _PenelopeProgramDebBuilder

# Globals and constants variables.

class PenepmaDebBuilder(_PenelopeProgramDebBuilder):

    def __init__(self, zip_path):
        if not os.path.basename(zip_path).startswith('PENEPMA'):
            raise ValueError('Zip file should be the PENEPMA-*.zip')
        self._penepma_zip_path = zip_path

        self._penelope_zip_path = zip_path.replace('PENEPMA', 'PENELOPE')
        if not os.path.exists(self._penelope_zip_path):
            raise ValueError('Cannot find PENELOPE-*.zip')

        _PenelopeProgramDebBuilder.__init__(self, zip_path,
                                            package='penelope-penepma',
                                            fullname='PENEPMA main program',
                                            short_description='Monte Carlo code for the simulation of x-ray emission spectra using PENELOPE',
                                            long_description="The computer program penepma performs Monte Carlo simulations of x-ray emission spectra from complex material structures irradiated by monoenergetic electron beams. The program uses the general-purpose Monte Carlo code system penelope (version 2008) for electron and photon transport, which implements the most elaborate interaction models available for arbitrary materials. The structure and operation of penepma are similar to those of the generic main program penmain, which is part of the penelope distribution package. penepma is designed to allow occasional users to simulate EPMA experiments and x-ray generators without having to write a penelope main program. The user defines the details of his or her experiment (electron-beam characteristics, geometrical structure and composition of the target, photon detectors) and the simulation control parameters by editing the input file. The program delivers energy spectra of photons that enter the various detectors, as well as characteristic line intensities, with fluorescence contributions given separately. Optionally, penepma can generate a three-dimensional distribution of x-ray generation.",
                                            depends=['libc6'],
                                            recommends=['penelope-pendbase', 'penelope-material', 'gnuplot'])

    def _extract_zip(self, temp_dir, *args, **kwargs):
        # PENELOPE
        with zipfile.ZipFile(self._penelope_zip_path, 'r') as z:
            for filename in z.namelist():
                if filename.startswith('penelope/fsource'):
                    z.extract(filename, temp_dir)

        # PENEPMA
        with zipfile.ZipFile(self._penepma_zip_path, 'r') as z:
            z.extractall(temp_dir)

    def _create_folder_structure(self, temp_dir, *args, **kwargs):
        _PenelopeProgramDebBuilder._create_folder_structure(self, temp_dir, *args, **kwargs)
        os.makedirs(os.path.join(temp_dir, 'usr', 'share', self._package, 'gnuplot_scripts'))

    def _compile_penepma(self, temp_dir, *args, **kwargs):
        src = os.path.join(temp_dir, 'penepma', 'programs', 'penepma.f')
        dst = os.path.join(temp_dir, 'penelope', 'fsource')
        shutil.copy(src, dst)

        filepath = os.path.join(temp_dir, 'penelope', 'fsource', 'penepma.f')
        outfilepath = self._compile(temp_dir, filepath, *args, **kwargs)

        dst = os.path.join(temp_dir, 'usr', 'bin')
        shutil.copy(outfilepath, dst)

    def _compile_convolg(self, temp_dir, *args, **kwargs):
        filepath = os.path.join(temp_dir, 'penepma', 'convolg', 'convolg.f')
        outfilepath = self._compile(temp_dir, filepath, *args, **kwargs)

        dst = os.path.join(temp_dir, 'usr', 'bin')
        shutil.copy(outfilepath, dst)

    def _compile_penepma_sum(self, temp_dir, *args, **kwargs):
        filepath = os.path.join(temp_dir, 'penepma', 'programs', 'sum_runs', 'penepma_sum.f')
        outfilepath = self._compile(temp_dir, filepath, *args, **kwargs)

        dst = os.path.join(temp_dir, 'usr', 'bin')
        shutil.copy(outfilepath, dst)

    def _reorganize_files(self, temp_dir, *args, **kwargs):
        # Examples
        src = os.path.join(temp_dir, 'penepma', 'examples')
        dst = os.path.join(temp_dir, 'usr', 'share', self._package)
        shutil.move(src, dst)

        # Gnuplot
        dst = os.path.join(temp_dir, 'usr', 'share', self._package, 'gnuplot_scripts')
        for src in glob.iglob(os.path.join(temp_dir, 'penepma', 'programs', '*.gnu')):
            shutil.move(src, dst)

        src = os.path.join(temp_dir, 'penepma', 'convolg', 'convolg.gnu')
        shutil.move(src, dst)

        # Doc
        src = os.path.join(temp_dir, 'penepma', 'report', 'penepma.pdf')
        dst = os.path.join(temp_dir, 'usr', 'share', 'doc', self._package)
        shutil.move(src, dst)

        # Cleanup
        shutil.rmtree(os.path.join(temp_dir, 'penelope'))
        shutil.rmtree(os.path.join(temp_dir, 'penepma'))

    def _build(self, temp_dir, *args, **kwargs):
        self._extract_zip(temp_dir, *args, **kwargs)

        self._create_folder_structure(temp_dir, *args, **kwargs)

        self._compile_penepma(temp_dir, *args, **kwargs)

        manpage = self._create_man_page(temp_dir, 'penepma',
                                        short_description='Performs Monte Carlo simulation of electron-probe microanalysis (EPMA) measurements',
                                        synopsis='.B penepma\n< inputfile.in',
                                        *args, **kwargs)
        self._write_man_page(manpage, temp_dir, *args, **kwargs)

        self._compile_convolg(temp_dir, *args, **kwargs)

        manpage = self._create_man_page(temp_dir, 'convolg',
                                        short_description='Generates the channel number spectrum of a detector from the energy spectrum of incident photons.',
                                        long_description='The channel number spectrum is obtained as the convolution of the energy spectrum of incident photons with the detector resolution function.\nThe incident energy spectrum, which is considered as a histogram, is read from an input file. Energy bins are assumed to have uniform width. Each line in the input file contains the centre of the energy bin (in eV) and the bar height. The energy bin centers must be in increasing order.\nThe energy resolution function of the detector is assumed to be a Gaussian distribution with mean equal to the incident photon energy E. Its full width at half maximum (a function of E) is given by the external function FWHM(E), to be defined by the user. The present version of function FWHM(E) corresponds to a typical Si(Li) detector.',
                                        synopsis='.B convolg',
                                        *args, **kwargs)
        self._write_man_page(manpage, temp_dir, *args, **kwargs)

        self._compile_penepma_sum(temp_dir, *args, **kwargs)

        manpage = self._create_man_page(temp_dir, 'penepma_sum',
                                        short_description="Adds the values of the counters in a number of dump files generated from independent runs of PENEPMA",
                                        long_description="It allows the user to run the same problem in several processors, using different seeds of the random number generator, and then combine the results to produce a single set of output files, with accumulated statistics. It works as an effective \"poor man's\" parallelization device.",
                                        synopsis='.B penepma_sum\n< inputfile.in\n\ninputfile.in must contain the list of relative paths and filenames of the dump files (one file in each line). All dump files must correspond to the same problem, that is, they must result from PENEPMA simulations with input files that differ only in the seeds of the random number generator. The responsibility of ensuring that the dump files do correspond to the same problem rests with the user.',
                                        *args, **kwargs)
        self._write_man_page(manpage, temp_dir, *args, **kwargs)

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
