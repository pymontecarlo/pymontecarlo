#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.util.transition import \
    (Transition, get_transitions, K_family, L_family, M_family, N_family,
     Ka, Kb, La, Lb, Lg, Ma, Mb, Mg, shell_transitions)
from pymontecarlo.util.subshell import get_subshell

# Globals and constants variables.
from pymontecarlo.util.transition import _SUBSHELLS, _SIEGBAHNS_NOGREEK, _SIEGBAHNS


class TestTransition(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        for i, shells in enumerate(_SUBSHELLS):
            x = Transition(13, shells[0], shells[1])
            setattr(self, 'x%i' % i, x)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def test__init__subshells(self):
        x = Transition(13, get_subshell(4), get_subshell(1))
        self.assertEqual(13, x.z)
        self.assertEqual("Al Ka1", str(x))

    def test__init__siegbahn(self):
        x = Transition(13, siegbahn="La1")
        self.assertEqual(13, x.z)
        self.assertEqual("Al La1", str(x))

    def test__str__(self):
        for i, siegbahn in enumerate(_SIEGBAHNS_NOGREEK):
            x = getattr(self, "x%i" % i)
            self.assertEqual("Al " + siegbahn, str(x))

    def test__unicode__(self):
        for i, siegbahn in enumerate(_SIEGBAHNS):
            x = getattr(self, "x%i" % i)
            self.assertEqual("Al " + siegbahn, unicode(x))

    def testfrom_xml(self):
        element = self.x0.to_xml()
        x0 = Transition.from_xml(element)

        self.assertEqual(13, x0.z)
        self.assertEqual('Al Ka1', str(x0))

    def testz(self):
        for i in range(len(_SUBSHELLS)):
            x = getattr(self, "x%i" % i)
            self.assertEqual(13, x.z)
            self.assertEqual(13, x.atomicnumber)

    def testsrc(self):
        for i, shells in enumerate(_SUBSHELLS):
            x = getattr(self, "x%i" % i)
            self.assertEqual(get_subshell(shells[0]), x.src)

    def testdest(self):
        for i, shells in enumerate(_SUBSHELLS):
            x = getattr(self, "x%i" % i)
            self.assertEqual(get_subshell(shells[1]), x.dest)

    def testiupac(self):
        for i, shells in enumerate(_SUBSHELLS):
            x = getattr(self, "x%i" % i)
            src = get_subshell(shells[0])
            dest = get_subshell(shells[1])
            self.assertEqual('-'.join([src.iupac, dest.iupac]), x.iupac)

    def testsiegbahn(self):
        for i, siegbahn in enumerate(_SIEGBAHNS):
            x = getattr(self, "x%i" % i)
            self.assertEqual(siegbahn, x.siegbahn)

    def testenergy(self):
        self.assertAlmostEqual(1486.3, self.x1.energy, 4)

    def testprobability(self):
        self.assertAlmostEqual(0.0123699, self.x1.probability, 4)

    def testexists(self):
        self.assertTrue(self.x1.exists())
        self.assertFalse(self.x29.exists())

    def testto_xml(self):
        element = self.x0.to_xml()

        self.assertEqual(13, int(element.get('z')))
        self.assertEqual(4, int(element.get('src')))
        self.assertEqual(1, int(element.get('dest')))

class TestModule(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testget_transitions(self):
        transitions = get_transitions(13)
        self.assertEqual(11, len(transitions))

        transitions = get_transitions(13, 1e3, 2e3)
        self.assertEqual(4, len(transitions))

    def testfamily(self):
        # K
        transitions = K_family(13)
        self.assertEqual(4, len(transitions))
        for transition in transitions:
            self.assertEqual('K', transition.dest.family)

        # L
        transitions = L_family(29)
        self.assertEqual(14, len(transitions))
        for transition in transitions:
            self.assertEqual('L', transition.dest.family)

        # M
        transitions = M_family(79)
        self.assertEqual(22, len(transitions))
        for transition in transitions:
            self.assertEqual('M', transition.dest.family)

        # N
        transitions = N_family(92)
        self.assertEqual(2, len(transitions))
        for transition in transitions:
            self.assertEqual('N', transition.dest.family)

    def testgroups(self):
        # Ka
        transitions = Ka(79)
        self.assertEqual(2, len(transitions))

        # Kb
        transitions = Kb(79)
        self.assertEqual(2, len(transitions))

        # La
        transitions = La(79)
        self.assertEqual(2, len(transitions))

        # Lb
        transitions = Lb(79)
        self.assertEqual(11, len(transitions))

        # Lg
        transitions = Lg(79)
        self.assertEqual(9, len(transitions))

        # Ma
        transitions = Ma(79)
        self.assertEqual(2, len(transitions))

        # Mb
        transitions = Mb(79)
        self.assertEqual(1, len(transitions))

        # Mg
        transitions = Mg(79)
        self.assertEqual(1, len(transitions))

    def testshell_transitions(self):
        transitions = shell_transitions(79, dest=1)
        self.assertEqual(K_family(79), transitions)

        transitions = set()
        transitions |= shell_transitions(79, dest=2)
        transitions |= shell_transitions(79, dest=3)
        transitions |= shell_transitions(79, dest=4)
        self.assertEqual(L_family(79), transitions)

        transitions = shell_transitions(79, dest=[2, 3, 4])
        self.assertEqual(L_family(79), transitions)

        transitions = set()
        transitions |= shell_transitions(79, dest=5)
        transitions |= shell_transitions(79, dest=6)
        transitions |= shell_transitions(79, dest=7)
        transitions |= shell_transitions(79, dest=8)
        transitions |= shell_transitions(79, dest=9)
        self.assertEqual(M_family(79), transitions)

        transitions = shell_transitions(79, dest=[5, 6, 7, 8, 9])
        self.assertEqual(M_family(79), transitions)

        transitions = shell_transitions(79, src=4, dest=1)
        self.assertEqual(1, len(transitions))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
