#!/usr/bin/env python
"""
================================================================================
:mod:`relaxation_data` -- Subshell, transition and relaxation data
================================================================================

.. module:: relaxation_data
   :synopsis: ubshell, transition and relaxation data

.. inheritance-diagram:: pymontecarlo.utils.relaxation_data

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
from pymontecarlo.util.xmlobj import XMLObject
import pymontecarlo.util.element_properties as ep

# Globals and constants variables.
SHELL_IUPACS = ["K",
                "L1", "L2", "L3",
                "M1", "M2", "M3", "M4", "M5",
                "N1", "N2", "N3", "N4", "N5", "N6", "N7",
                "O1", "O2", "O3", "O4", "O5", "O6", "O7",
                "P1", "P2", "P3", "P4", "P5",
                "Q1", "OUTER"]

SHELL_SIEGBAHNS = ["K",
                   "LI", "LII", "LIII",
                   "MI", "MII", "MIII", "MIV", "MV",
                   "NI", "NII", "NIII", "NIV", "NV", "NVI", "NVII",
                   "OI", "OII", "OIII", "OIV", "OV", "OVI", "OVII",
                   "PI", "PII", "PIII", "PIV", "PV",
                   "QI", "OUTER"]

SHELL_ORBITALS = ["1s1/2",
                  "2s1/2", "2p1/2", "2p3/2",
                  "3s1/2", "3p1/2", "3p3/2", "3d3/2", "3d5/2",
                  "4s1/2", "4p1/2", "4p3/2", "4d3/2", "4d5/2", "4f5/2", "4f7/2",
                  "5s1/2", "5p1/2", "5p3/2", "5d3/2", "5d5/2", "5f5/2", "5f7/2",
                  "6s1/2", "6p1/2", "6p3/2", "6d3/2", "6d5/2",
                  "7s1/2", ""]

TRANSITION_SHELLS = \
    [('K', 'L3'), ('K', 'L2'), ('K', 'M3'), ('K', 'N3'), ('K', 'M2'),
     ('K', 'N5'), ('K', 'M5'), ('L3', 'N2'), ('L3', 'N3'), ('L3', 'O2'),
     ('L3', 'O3'), ('L3', 'P1'), ('L3', 'M5'), ('L3', 'M4'),
     ('L3', 'N4'), ('L3', 'N5'), ('L3', 'O4'), ('L3', 'N1'),
     ('L3', 'O1'), ('L3', 'M1'), ('L3', 'M3'), ('L3', 'M2'),
     ('L3', 'N6'), ('L2', 'M2'), ('L2', 'M5'), ('L2', 'N2'),
     ('L2', 'N3'), ('L2', 'N5'), ('L2', 'O2'), ('L2', 'O3'),
     ('L2', 'P2'), ('L2', 'M4'), ('L2', 'M3'), ('L2', 'N4'),
     ('L2', 'N1'), ('L2', 'O4'), ('L2', 'O1'), ('L2', 'M1'),
     ('L2', 'N6'), ('L1', 'M1'), ('L1', 'N1'), ('L1', 'N4'),
     ('L1', 'O1'), ('L1', 'O4'), ('L1', 'M4'), ('L1', 'M3'),
     ('L1', 'M2'), ('L1', 'M5'), ('L1', 'N2'), ('L1', 'N5'),
     ('L1', 'N3'), ('L1', 'O3'), ('L1', 'O2'), ('M1', 'N2'),
     ('M1', 'N3'), ('M2', 'M4'), ('M2', 'N1'), ('M2', 'N4'),
     ('M2', 'O4'), ('M3', 'M4'), ('M3', 'M5'), ('M3', 'N1'),
     ('M3', 'N4'), ('M3', 'O1'), ('M3', 'O4'), ('M3', 'O5'),
     ('M3', 'N5'), ('M4', 'N3'), ('M4', 'O2'), ('M4', 'N6'),
     ('M4', 'N2'), ('M5', 'O3'), ('M5', 'N7'), ('M5', 'N6'),
     ('M5', 'N3'), ('N4', 'N6'), ('N5', 'N6')]

TRANSITION_SIEGBAHNS = \
    [u"K\u03B11", u"K\u03B12", u"K\u03B21", u"K\u03B22", u"K\u03B23",
     u"K\u03B24", u"K\u03B25", "L3N2", "L3N3", "L3O2", "L3O3", "L3P1",
     u"L\u03B11", u"L\u03B12", u"L\u03B215", u"L\u03B22", u"L\u03B25",
     u"L\u03B26", u"L\u03B27", u"L\u2113", "Ls", "Lt", "Lu", "L2M2",
     "L2M5", "L2N2", "L2N3", "L2N5", "L2O2", "L2O3", "L2P2",
     u"L\u03B21", u"L\u03B217", u"L\u03B31", u"L\u03B35", u"L\u03B36",
     u"L\u03B38", u"L\u03B7", u"L\u03BD", "L1M1", "L1N1", "L1N4",
     "L1O1", "L1O4/L1O5", u"L\u03B210", u"L\u03B23", u"L\u03B24",
     u"L\u03B29", u"L\u03B32", u"L\u03B311", u"L\u03B33", u"L\u03B34",
     u"L\u03B34p", "M1N2", "M1N3", "M2M4", "M2N1", "M2N4", "M2O4",
     "M3M4", "M3M5", "M3N1", "M3N4", "M3O1", "M3O4", "M3O5",
     u"M\u03B3", "M4N3", "M4O2", u"M\u03B2", u"M\u03B62", "M5O3",
     u"M\u03B11", u"M\u03B12", u"M\u03B61", "N4N6", "N5N6/N5N7"]

TRANSITION_SIEGBAHNS_NOGREEK = \
    ['Ka1', 'Ka2', 'Kb1', 'Kb2', 'Kb3', 'Kb4', 'Kb5', 'L3N2', 'L3N3', 'L3O2',
     'L3O3', 'L3P1', 'La1', 'La2', 'Lb15', 'Lb2', 'Lb5', 'Lb6', 'Lb7', 'Ll',
     'Ls', 'Lt', 'Lu', 'L2M2', 'L2M5', 'L2N2', 'L2N3', 'L2N5', 'L2O2', 'L2O3',
     'L2P2', 'Lb1', 'Lb17', 'Lg1', 'Lg5', 'Lg6', 'Lg8', 'Le', 'Lv',
     'L1M1', 'L1N1', 'L1N4', 'L1O1', 'L1O4/L1O5', 'Lb10', 'Lb3', 'Lb4', 'Lb9',
     'Lg2', 'Lg11', 'Lg3', 'Lg4', 'Lg4p', 'M1N2', 'M1N3', 'M2M4', 'M2N1',
     'M2N4', 'M2O4', 'M3M4', 'M3M5', 'M3N1', 'M3N4', 'M3O1', 'M3O4', 'M3O5',
     'Mg', 'M4N3', 'M4O2', 'Mb', 'Mz2', 'M5O3', 'Ma1', 'Ma2', 'Mz1',
     'N4N6', 'N5N6/N5N7']

class Subshell(object):
    def __init__(self, index=None, orbital=None, iupac=None, siegbahn=None):
        """
        An atomic subshell. Only one of the following arguments must be 
        defined:
        
        :arg index: index of the subshell between 1 (K) and 30 (outer)
        :arg orbital: orbital of the subshell (e.g. 1s1/2)
        :arg iupac: IUPAC symbol of the subshell
        :arg siegbahn: Siegbahn symbol of the subshell
        
        If more than one argument is given, only the first one is used to create
        the subshell.
        """
        if index is not None:
            if index < 1 or index > 30:
                raise ValueError, "Id (%s) must be between [1, 30]." % index
            index -= 1
        elif orbital is not None:
            orbital = orbital.lower()

            try:
                index = SHELL_ORBITALS.index(orbital)
            except ValueError:
                raise ValueError, "Unknown orbital (%s). Possible orbitals: %s" % \
                        (orbital, SHELL_ORBITALS)
        elif iupac is not None:
            iupac = iupac.upper()

            try:
                index = SHELL_IUPACS.index(iupac)
            except ValueError:
                raise ValueError, "Unknown IUPAC (%s). Possible IUPAC: %s" % \
                        (iupac, SHELL_IUPACS)
        elif siegbahn is not None:
            siegbahn = siegbahn.upper()

            try:
                index = SHELL_SIEGBAHNS.index(siegbahn)
            except ValueError:
                raise ValueError, "Unknown Siegbahn (%s). Possible Siegbahn: %s" % \
                        (siegbahn, SHELL_SIEGBAHNS)
        else:
            raise ValueError, "You must specify an index, orbital, IUPAC or Siegbahn"

        self._index = index + 1
        self._orbtial = SHELL_ORBITALS[index]
        self._iupac = SHELL_IUPACS[index]
        self._siegbahn = SHELL_SIEGBAHNS[index]

        if index != 29:
            self._family = self._iupac[0].upper()
        else:
            self._family = None

    def __repr__(self):
        return '<Subshell(index=%i)>' % self.index

    def __str__(self):
        return self._iupac

    def __unicode__(self):
        return self._iupac

    def __eq__(self, other):
        return self._index == other._index

    def __ne__(self, other):
        return self._index != other._index

    def __cmp__(self, other):
        return cmp(self._index, other._index)

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

class Transition(XMLObject):
    def __init__(self, z, src=None, dest=None, siegbahn=None):
        """
        Creates a new transition from a source and destination subshells 
        or from its Siegbahn symbol::
        
           t = Transition(29, 4, 1)
           t = Transition(29, siegbahn='Ka1')
           
        :arg z: atomic number
        :arg src: source subshell
        :arg dest: destination subshell
        :arg siegbahn: Siegbahn symbol
        """
        if src is not None and dest is not None:
            if src < dest:
                raise ValueError, "The source subshell (%s) must be greater " + \
                        "than the destination subshell (%s)" % (src, dest)

            try:
                index = TRANSITION_SHELLS.index((dest.iupac, src.iupac))
            except ValueError:
                raise ValueError, "Unknown transition (%s, %s)" % \
                        (dest.iupac, src.iupac)
        elif siegbahn is not None:
            if isinstance(siegbahn, unicode):
                table = TRANSITION_SIEGBAHNS
            else:
                table = TRANSITION_SIEGBAHNS_NOGREEK

            try:
                index = table.index(siegbahn)
            except ValueError:
                raise ValueError, "Unknown transition (%s)" % siegbahn
        else:
            raise ValueError, "Specify shells or siegbahn"

        self._index = index
        dest, src = TRANSITION_SHELLS[index]
        self._src = Subshell(iupac=src)
        self._dest = Subshell(iupac=dest)
        self._iupac = '-'.join(TRANSITION_SHELLS[index])
        self._siegbahn = unicode(TRANSITION_SIEGBAHNS[index])
        self._siegbahn_nogreek = TRANSITION_SIEGBAHNS_NOGREEK[index]
        self._z = z
        self._symbol = ep.symbol(z)

    def __repr__(self):
        return '<Transition(%s %s)>' % (self._symbol, self._siegbahn_nogreek)

    def __str__(self):
        return "%s %s" % (self._symbol, self._siegbahn_nogreek)

    def __unicode__(self):
        return u"%s %s" % (self._symbol, self._siegbahn)

    def __eq__(self, other):
        return self._index == other._index and self._z == other._z

    def __ne__(self, other):
        return self._index != other._index or self._z != other._z

    def __cmp__(self, other):
        c = cmp(self._z, other._z)
        if c != 0:
            return c

        return cmp(self._index, other._index)

    def __hash__(self):
        return hash((self._z, self._index))

    @classmethod
    def from_xml(cls, element):
        z = int(element.get('z'))
        src = int(element.get('src'))
        dest = int(element.get('dest'))

        return cls(z, Subshell(index=src), Subshell(index=dest))

    @property
    def z(self):
        """
        Atomic number of this transition.
        """
        return self._z

    atomicnumber = z

    @property
    def src(self):
        """
        Source shell of this transition.
        """
        return self._src

    @property
    def dest(self):
        """
        Destination shell of this transition.
        """
        return self._dest

    @property
    def iupac(self):
        """
        IUPAC symbol of this transition.
        """
        return self._iupac

    @property
    def siegbahn(self):
        """
        Seigbahn symbol of this transition.
        """
        return self._siegbahn

    def to_xml(self):
        element = XMLObject.to_xml(self)

        element.set('z', str(self.z))
        element.set('src', str(self.src.index))
        element.set('dest', str(self.dest.index))

        return element

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
            fileobj = resource_stream(__name__, 'relaxation_data.csv')

        self.data = self._read(fileobj)

    def _read(self, fileobj):
        data = {}
        reader = csv.reader(fileobj)

        for row in reader:
            z = int(row[0])
            subshell0 = int(row[1])
            subshell1 = int(row[2])

            probability = float(row[3])
            energy_eV = float(row[4])

            data.setdefault(z, {})
            data[z].setdefault(subshell0, {})
            data[z][subshell0].setdefault(subshell1, {})
            data[z][subshell0][subshell1][self.KEY_ENERGY] = energy_eV

            if probability >= 0:
                data[z][subshell0][subshell1][self.KEY_PROBABILITY] = probability

        return data

    def _get_value(self, key, z=None, subshells=None, transition=None):
        if z is None:
            z = transition.z
        if subshells is None:
            subshells = transition.dest.index, transition.src.index

        if not z in self.data:
            raise ValueError, "No relaxation data for atomic number %i." % z

        try:
            return self.data[z][subshells[0]][subshells[1]][key]
        except KeyError:
            return 0.0

    def energy(self, z=None, subshells=None, transition=None):
        """
        Returns the energy of a transition in eV.
        One can either specified the atomic number and subshells or an atomic
        transition object.
        
        :arg z: atomic number (3 to 99)
        :arg subshells: :class:`tuple` of length 2 of the destination and 
            source subshells id (between 1 and 30)
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
        :arg subshells: :class:`tuple` of length 2 of the destination and 
            source subshells id (between 1 and 30)
        :arg transition: atomic transition
        :type transition: :class:`.Transition`
        """
        return self._get_value(self.KEY_PROBABILITY, z, subshells, transition)

    def transitions(self, z, energyLow=0.0, energyHigh=1e6):
        """
        Returns all the X-ray transitions for the specified atomic number if
        the energy of these transitions is between the specified energy limits.
        The energy limits are inclusive.
        
        :arg z: atomic number (3 to 99)
        :arg energyLow: lower energy limit in eV (default: 0 eV)
        :arg energyHigh: upper energy limit in eV (default: 1 MeV)
        """
        transitions = []

        atom_data = self.data.get(z, {})

        for subshell0 in atom_data:
            dest = Subshell(index=subshell0)

            for subshell1 in atom_data[subshell0]:
                energy = atom_data[subshell0][subshell1][self.KEY_ENERGY]
                if energy < energyLow or energy > energyHigh:
                    continue

                src = Subshell(index=subshell1)

                try:
                    transition = Transition(z, src, dest)
                except ValueError:
                    continue # skip unknown transition
                else:
                    transitions.append(transition)

        return sorted(transitions)
