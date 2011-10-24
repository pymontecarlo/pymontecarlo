#!/usr/bin/env python
"""
================================================================================
:mod:`subshell` -- Atomic subshell
================================================================================

.. module:: subshell
   :synopsis: Atomic subshell

.. inheritance-diagram:: subshell

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.

# Local modules.

# Globals and constants variables.
_IUPACS = ["K",
           "L1", "L2", "L3",
           "M1", "M2", "M3", "M4", "M5",
           "N1", "N2", "N3", "N4", "N5", "N6", "N7",
           "O1", "O2", "O3", "O4", "O5", "O6", "O7",
           "P1", "P2", "P3", "P4", "P5",
           "Q1", "OUTER"]

_SIEGBAHNS = ["K",
              "LI", "LII", "LIII",
              "MI", "MII", "MIII", "MIV", "MV",
              "NI", "NII", "NIII", "NIV", "NV", "NVI", "NVII",
              "OI", "OII", "OIII", "OIV", "OV", "OVI", "OVII",
              "PI", "PII", "PIII", "PIV", "PV",
              "QI", "OUTER"]

_ORBITALS = ["1s1/2",
             "2s1/2", "2p1/2", "2p3/2",
             "3s1/2", "3p1/2", "3p3/2", "3d3/2", "3d5/2",
             "4s1/2", "4p1/2", "4p3/2", "4d3/2", "4d5/2", "4f5/2", "4f7/2",
             "5s1/2", "5p1/2", "5p3/2", "5d3/2", "5d5/2", "5f5/2", "5f7/2",
             "6s1/2", "6p1/2", "6p3/2", "6d3/2", "6d5/2",
             "7s1/2", ""]

class __Subshell(object):
    def __init__(self, index):
        """
        Creates an atomic subshell. 
        
        :arg index: index of the subshell between 1 (K) and 30 (outer)
        """
        self._index = index
        self._orbtial = _ORBITALS[index - 1]
        self._iupac = _IUPACS[index - 1]
        self._siegbahn = _SIEGBAHNS[index - 1]

        if index != 30:
            self._family = self._iupac[0].upper()
        else:
            self._family = None

    def __repr__(self):
        return '<Subshell(index=%i)>' % self.index

    def __str__(self):
        return self._iupac

    def __unicode__(self):
        return self._iupac

    def __hash__(self):
        return hash(("Subshell", self._index))

    def __eq__(self, other):
        return self._index == other._index

    def __ne__(self, other):
        return self._index != other._index

    def __cmp__(self, other):
        return cmp(self._index, other._index)

    def __copy__(self):
        return self

    def __deepcopy__(self, memo=None):
        return self

    @property
    def index(self):
        """
        Index of this subshell between 1 (K) and 30 (outer).
        """
        return self._index

    @property
    def orbital(self):
        """
        Orbital of this subshell.
        """
        return self._orbtial

    @property
    def iupac(self):
        """
        IUPAC symbol of this subshell.
        """
        return self._iupac

    @property
    def siegbahn(self):
        """
        Siegbahn symbol of this subshell.
        """
        return self._siegbahn

    @property
    def family(self):
        """
        Family of this subshell. 
        Either K, L, M, N, O, P, Q.
        The family of the outer subshell is ``None``. 
        """
        return self._family

__subshells = {}
for i in range(1, 31):
    __subshells[i] = __Subshell(i)

def get_subshell(index=None, orbital=None, iupac=None, siegbahn=None):
    """
    An atomic subshell. Only one of the following arguments must be
        defined:

        :arg index: index of the subshell between 1 (K) and 30 (outer)
        :arg orbital: orbital of the subshell (e.g. 1s1 / 2)
        :arg iupac: IUPAC symbol of the subshell
        :arg siegbahn: Siegbahn symbol of the subshell

        If more than one argument is given, only the first one is used to create
        the subshell.
    """
    if index is not None:
        if index < 1 or index > 30:
            raise ValueError, "Id (%s) must be between [1, 30]." % index
    elif orbital is not None:
        try:
            index = _ORBITALS.index(orbital.lower()) + 1
        except ValueError:
            raise ValueError, "Unknown orbital (%s). Possible orbitals: %s" % \
                    (orbital, _ORBITALS)
    elif iupac is not None:
        try:
            index = _IUPACS.index(iupac.upper()) + 1
        except ValueError:
            raise ValueError, "Unknown IUPAC (%s). Possible IUPAC: %s" % \
                    (iupac, _IUPACS)
    elif siegbahn is not None:
        try:
            index = _SIEGBAHNS.index(siegbahn.upper()) + 1
        except ValueError:
            raise ValueError, "Unknown Siegbahn (%s). Possible Siegbahn: %s" % \
                    (siegbahn, _SIEGBAHNS)
    else:
        raise ValueError, "You must specify an index, orbital, IUPAC or Siegbahn"

    return __subshells[index]

