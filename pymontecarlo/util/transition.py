#!/usr/bin/env python
"""
================================================================================
:mod:`transition` -- Atomic transition
================================================================================

.. module:: transition
   :synopsis: Atomic transition

.. inheritance-diagram:: transition

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from operator import methodcaller, attrgetter

# Third party modules.

# Local modules.
from pymontecarlo.util.xmlobj import XMLObject
import pymontecarlo.util.element_properties as ep
from pymontecarlo.util.subshell import get_subshell
from pymontecarlo.util.relaxation_data import relaxation_data

# Globals and constants variables.
_ZGETTER = attrgetter('z')

"""
Subshells (source -> destination) of all transitions.
"""
_SUBSHELLS = \
    [(4, 1) , (3, 1) , (7, 1) , (12, 1), (6, 1) , (14, 1) , (9, 1) ,
     (11, 4), (12, 4), (18, 4), (19, 4), (24, 4), (9, 4)  , (8, 4) ,
     (13, 4), (14, 4), (20, 4), (10, 4), (17, 4), (5, 4)  , (7, 4) ,
     (6, 4) , (15, 4), (6, 3) , (9, 3) , (11, 3), (12, 3) , (14, 3),
     (18, 3), (19, 3), (25, 3), (8, 3) , (7, 3) , (13, 3) , (10, 3),
     (20, 3), (17, 3), (5, 3) , (15, 3), (5, 2) , (10, 2) , (13, 2),
     (17, 2), (20, 2), (8, 2) , (7, 2) , (6, 2) , (9, 2)  , (11, 2),
     (14, 2), (12, 2), (19, 2), (18, 2), (11, 5), (12, 5) , (8, 6) ,
     (10, 6), (13, 6), (20, 6), (8, 7) , (9, 7) , (10, 7) , (13, 7),
     (17, 7), (20, 7), (21, 7), (14, 7), (12, 8), (18, 8) , (15, 8),
     (11, 8), (19, 9), (16, 9), (15, 9), (12, 9), (15, 13), (15, 14)]

_SIEGBAHNS = \
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

_SIEGBAHNS_NOGREEK = \
    ['Ka1', 'Ka2', 'Kb1', 'Kb2', 'Kb3', 'Kb4', 'Kb5', 'L3N2', 'L3N3', 'L3O2',
     'L3O3', 'L3P1', 'La1', 'La2', 'Lb15', 'Lb2', 'Lb5', 'Lb6', 'Lb7', 'Ll',
     'Ls', 'Lt', 'Lu', 'L2M2', 'L2M5', 'L2N2', 'L2N3', 'L2N5', 'L2O2', 'L2O3',
     'L2P2', 'Lb1', 'Lb17', 'Lg1', 'Lg5', 'Lg6', 'Lg8', 'Le', 'Lv',
     'L1M1', 'L1N1', 'L1N4', 'L1O1', 'L1O4/L1O5', 'Lb10', 'Lb3', 'Lb4', 'Lb9',
     'Lg2', 'Lg11', 'Lg3', 'Lg4', 'Lg4p', 'M1N2', 'M1N3', 'M2M4', 'M2N1',
     'M2N4', 'M2O4', 'M3M4', 'M3M5', 'M3N1', 'M3N4', 'M3O1', 'M3O4', 'M3O5',
     'Mg', 'M4N3', 'M4O2', 'Mb', 'Mz2', 'M5O3', 'Ma1', 'Ma2', 'Mz1',
     'N4N6', 'N5N6/N5N7']

class Transition(XMLObject):
    def __init__(self, z, src=None, dest=None, siegbahn=None):
        """
        Creates a new transition from a source and destination subshells 
        or from its Siegbahn symbol::
        
           t = Transition(29, 4, 1)
           t = Transition(29, siegbahn='Ka1')
           
        :arg z: atomic number (from 3 to 99 inclusively)
        :arg src: source subshell index between 1 (K) and 30 (outer) or subshell object
        :arg dest: destination subshell index between 1 (K) and 30 (outer) or subshell object
        :arg siegbahn: Siegbahn symbol
        """
        if src is not None and dest is not None:
            if src < dest:
                raise ValueError, "The source subshell (%s) must be greater " + \
                        "than the destination subshell (%s)" % (src, dest)

            if hasattr(src, 'index'): src = src.index
            if hasattr(dest, 'index'): dest = dest.index

            try:
                index = _SUBSHELLS.index((src, dest))
            except ValueError:
                raise ValueError, "Unknown transition (%s -> %s)" % (src, dest)
        elif siegbahn is not None:
            if isinstance(siegbahn, unicode):
                table = _SIEGBAHNS
            else:
                table = _SIEGBAHNS_NOGREEK

            try:
                index = table.index(siegbahn)
            except ValueError:
                raise ValueError, "Unknown transition (%s)" % siegbahn
        else:
            raise ValueError, "Specify shells or siegbahn"

        self._index = index
        src, dest = _SUBSHELLS[index]

        self._src = get_subshell(src)
        self._dest = get_subshell(dest)
        self._iupac = '-'.join([self._src.iupac, self._dest.iupac])
        self._siegbahn = unicode(_SIEGBAHNS[index])
        self._siegbahn_nogreek = _SIEGBAHNS_NOGREEK[index]
        self._z = z
        self._symbol = ep.symbol(z)

        self._energy = relaxation_data.energy(z, (src, dest))
        self._probability = relaxation_data.probability(z, (src, dest))
        self._exists = relaxation_data.exists(z, (src, dest))

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
        return hash(('Transition', self._z, self._index))

    @classmethod
    def from_xml(cls, element):
        z = int(element.get('z'))
        src = int(element.get('src'))
        dest = int(element.get('dest'))

        return cls(z, src, dest)

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

    @property
    def energy(self):
        """
        Energy of this transition in eV.
        """
        return self._energy

    @property
    def probability(self):
        """
        Probability of this transition.
        """
        return self._probability

    def exists(self):
        return self._exists

    def to_xml(self):
        element = XMLObject.to_xml(self)

        element.set('z', str(self.z))
        element.set('src', str(self.src.index))
        element.set('dest', str(self.dest.index))

        return element

class transitionset(frozenset):

    def __new__(cls, z, name, transitions):
        # Required
        # See http://stackoverflow.com/questions/4850370/inheriting-behaviours-for-set-and-frozenset-seem-to-differ
        return frozenset.__new__(cls, transitions)

    def __init__(self, z, name, transitions):
        """
        Creates a frozen set (immutable) of transitions.
        The atomic number must be the same for all transitions. 
        
        :arg z: atomic number of all transitions
        :arg name: name of the set (e.g. ``Ka``)
        :arg transitions: transitions in the set
        """
        # Common z
        zs = map(_ZGETTER, transitions)
        if transitions and len(set(zs)) != 1:
            raise ValueError, "All transitions in a set must have the same atomic number"

        self._z = z
        self._name = '%s %s' % (ep.symbol(z), name)

        frozenset.__init__(transitions)

    def __repr__(self):
        return '<transitionset(%s: %s)>' % (self._name, ', '.join(map(str, sorted(self))))

    def __str__(self):
        return self._name

    @property
    def z(self):
        """
        Atomic number of this transition set.
        """
        return self._z

    atomicnumber = z

def get_transitions(z, energylow=0.0, energyhigh=1e6):
    """
    Returns all the X-ray transitions for the specified atomic number if
    the energy of these transitions is between the specified energy limits.
    The energy limits are inclusive.
    
    :arg z: atomic number (3 to 99)
    :arg energylow: lower energy limit in eV (default: 0 eV)
    :arg energyhigh: upper energy limit in eV (default: 1 MeV)
    """
    transitions = []

    for subshells in _SUBSHELLS:
        if not relaxation_data.exists(z, subshells):
            continue

        energy = relaxation_data.energy(z, subshells)
        if energy < energylow or energy > energyhigh:
            continue

        transitions.append(Transition(z, *subshells))

    return sorted(transitions)

def _group(z, key):
    transitions = []

    for siegbahn in _SIEGBAHNS_NOGREEK:
        if siegbahn.startswith(key):
            transitions.append(Transition(z, siegbahn=siegbahn))

    return transitionset(z, key, filter(methodcaller('exists'), transitions))

def _shell(z, dest):
    transitions = []

    for src, ddest in _SUBSHELLS:
        if ddest != dest: continue
        transitions.append(Transition(z, src, dest))

    name = get_subshell(dest).siegbahn

    return transitionset(z, name, filter(methodcaller('exists'), transitions))

def K_family(z):
    """
    Returns all transitions from the K family.
    """
    return _group(z, 'K')

def L_family(z):
    """
    Returns all transitions from the L family.
    """
    return _group(z, 'L')

def M_family(z):
    """
    Returns all transitions from the M family.
    """
    return _group(z, 'M')

def N_family(z):
    """
    Returns all transitions from the N family.
    """
    return _group(z, 'N')

def Ka(z):
    """
    Returns all transitions from the Ka group.
    """
    return _group(z, 'Ka')

def Kb(z):
    """
    Returns all transitions from the Kb group.
    """
    return _group(z, 'Ka')

def La(z):
    """
    Returns all transitions from the La group.
    """
    return _group(z, 'La')

def Lb(z):
    """
    Returns all transitions from the Lb group.
    """
    return _group(z, 'Lb')

def Lg(z):
    """
    Returns all transitions from the Lg group.
    """
    return _group(z, 'Lg')

def Ma(z):
    """
    Returns all transitions from the Ma group.
    """
    return _group(z, 'Ma')

def Mb(z):
    """
    Returns all transitions from the Mb group.
    """
    return _group(z, 'Mb')

def Mg(z):
    """
    Returns all transitions from the Mg group.
    """
    return _group(z, 'Mg')

def LI(z):
    """
    Returns all transitions ending on the L\ :sub:`I` shell.
    """
    return _shell(z, 2)

def LII(z):
    """
    Returns all transitions ending on the L\ :sub:`II` shell.
    """
    return _shell(z, 3)

def LIII(z):
    """
    Returns all transitions ending on the L\ :sub:`III` shell.
    """
    return _shell(z, 4)

def MI(z):
    """
    Returns all transitions ending on the M\ :sub:`I` shell.
    """
    return _shell(z, 5)

def MII(z):
    """
    Returns all transitions ending on the M\ :sub:`II` shell.
    """
    return _shell(z, 6)

def MIII(z):
    """
    Returns all transitions ending on the M\ :sub:`III` shell.
    """
    return _shell(z, 7)

def MIV(z):
    """
    Returns all transitions ending on the M\ :sub:`IV` shell.
    """
    return _shell(z, 8)

def MV(z):
    """
    Returns all transitions ending on the M\ :sub:`V` shell.
    """
    return _shell(z, 9)