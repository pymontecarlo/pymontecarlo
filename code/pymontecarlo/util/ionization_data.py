#!/usr/bin/env python
"""
================================================================================
:mod:`ionization_data` -- Ionization energies of atomic subshell
================================================================================

.. module:: ionization_data
   :synopsis: Ionization energies of atomic subshell

.. inheritance-diagram:: pymontecarlo.util.ionization_data

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import sys
import csv

# Third party modules.

# Local modules.

# Globals and constants variables.

class IonizationData(object):

    def __init__(self, fileobj=None):
        """
        Ionization energies of atomic subshell. 
        
        The relaxation data should be comma-separated with the following
        columns: atomic number, shell and ionization energy (in eV). 
            
        If *fileobj* is ``None`` the default relaxation data is loaded.
        The ionization energies are taken from T.A. Carlson, 'Photoelectron and 
        Auger Spectroscopy' (Plenum Press, New York and London, 1975).
        
        :arg fileobj: file-object containing the ionization energies.
        """
        if fileobj is None:
            # Weird bug in Windows when using pkgutil.get_data to retrieve
            # relaxation_data.csv. This is a quick fix.
            dirname = os.path.dirname(sys.modules[__name__].__file__)
            fileobj = open(os.path.join(dirname, 'data/ionization_data.csv'))

        self.data = self._read(fileobj)

    def _read(self, fileobj):
        data = {}
        reader = csv.reader(fileobj)
        reader.next() # skip header

        for row in reader:
            z = int(row[0])
            subshell = int(row[1])
            energy_eV = float(row[2])

            data.setdefault(z, {})
            data[z].setdefault(subshell, energy_eV)

        return data

    def energy_eV(self, z, subshell):
        """
        Returns the ionization energy of a subshell in eV.
        
        :arg z: atomic number (1 to 99)
        :arg subshell: index of the subshells (1 to 29 inclu.)
        """
        if not z in self.data:
            raise ValueError, "No ionization energy for atomic number %i." % z

        try:
            return self.data[z][subshell]
        except KeyError:
            return 0.0

    def exists(self, z, subshell):
        """
        Returns whether the subshell exists.
        
        :arg z: atomic number (1 to 99)
        :arg subshell: index of the subshells (1 to 29 inclu.)
        """
        try:
            self.data[z][subshell]
            return True
        except KeyError:
            return False

ionization_data = IonizationData()
