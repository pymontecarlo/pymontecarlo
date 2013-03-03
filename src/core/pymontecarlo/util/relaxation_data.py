#!/usr/bin/env python
"""
================================================================================
:mod:`relaxation_data` -- Subshell, transition and relaxation data
================================================================================

.. module:: relaxation_data
   :synopsis: ubshell, transition and relaxation data

.. inheritance-diagram:: pymontecarlo.util.relaxation_data

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import csv

# Third party modules.
from pkg_resources import resource_stream #@UnresolvedImport

# Local modules.

# Globals and constants variables.

class RelaxationData(object):
    KEY_PROBABILITY = 'probability'
    KEY_ENERGY = 'energy'

    def __init__(self, fileobj=None):
        """
        Relaxation data for singly-ionised atoms.
        
        The relaxation data should be comma-separated with the following
        columns: atomic number, destination shell, source shell, transition
        probability and transition energy (in eV). 
            
        If *fileobj* is ``None`` the default relaxation data is loaded.
        The relaxation data is taken from PENELOPE 2011, where the transition 
        probabilities and energies were extracted from the LLNL Evaluated 
        Atomic Data Library (Perkins et al. 1991). 
        Some energies values were replaced by more accurate, when available.
        The energies for Lithium, Beryllium and Boron were taken from the
        DTSA database.
        However, no probabilities are available for these elements.
        
        :arg fileobj: file-object containing the relaxation data.
        """
        if fileobj is None:
            fileobj = resource_stream(__name__, 'data/relaxation_data.csv')

        self.data = self._read(fileobj)

    def _read(self, fileobj):
        data = {}
        reader = csv.reader(fileobj)
        reader.next() # skip header

        for row in reader:
            z = int(row[0])
            subshell_dest = int(row[1])
            subshell_src = int(row[2])

            probability = float(row[3])
            energy_eV = float(row[4])

            data.setdefault(z, {})
            data[z].setdefault(subshell_src, {})
            data[z][subshell_src].setdefault(subshell_dest, {})

            data[z][subshell_src][subshell_dest][self.KEY_ENERGY] = energy_eV

            if probability >= 0:
                data[z][subshell_src][subshell_dest][self.KEY_PROBABILITY] = probability

        return data

    def _get_value(self, key, z=None, subshells=None, transition=None):
        if z is None:
            z = transition.z
        if subshells is None:
            subshells = transition.src.index, transition.dest.index

        if not z in self.data:
            raise ValueError, "No relaxation data for atomic number %i." % z

        try:
            return self.data[z][subshells[0]][subshells[1]][key]
        except KeyError:
            return 0.0

    def energy_eV(self, z=None, subshells=None, transition=None):
        """
        Returns the energy of a transition in eV.
        One can either specified the atomic number and subshells or an atomic
        transition object.
        
        :arg z: atomic number (3 to 99)
        :arg subshells: :class:`tuple` of length 2 of the source and 
            destination subshells id (between 1 and 30)
        :arg transition: atomic transition
        :type transition: :class:`.Transition`
        """
        return self._get_value(self.KEY_ENERGY, z, subshells, transition)

    def probability(self, z=None, subshells=None, transition=None):
        """
        Returns the probability of an transition.
        One can either specified the atomic number and subshells or an atomic
        transition object.
        
        :arg z: atomic number (6 to 99)
        :arg subshells: :class:`tuple` of length 2 of the source and 
            destination subshells id (between 1 and 30)
        :arg transition: atomic transition
        :type transition: :class:`.Transition`
        """
        return self._get_value(self.KEY_PROBABILITY, z, subshells, transition)

    def exists(self, z=None, subshells=None, transition=None):
        """
        Returns whether the transition exists.
        One can either specified the atomic number and subshells or an atomic
        transition object.
        
        :arg z: atomic number (6 to 99)
        :arg subshells: :class:`tuple` of length 2 of the source and 
            destination subshells id (between 1 and 30)
        :arg transition: atomic transition
        :type transition: :class:`.Transition`
        """
        if z is None:
            z = transition.z
        if subshells is None:
            subshells = transition.src.index, transition.dest.index

        try:
            self.data[z][subshells[0]][subshells[1]]
            return True
        except KeyError:
            return False

relaxation_data = RelaxationData()
