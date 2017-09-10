.. pyMonteCarlo documentation master file, created by
   sphinx-quickstart on Wed Jun 14 16:08:24 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pyMonteCarlo's documentation!
========================================

.. image:: https://img.shields.io/pypi/v/pymontecarlo.svg
.. image:: https://img.shields.io/travis/pymontecarlo/pymontecarlo.svg
.. image:: https://img.shields.io/codecov/c/github/pymontecarlo/pymontecarlo.svg

**pyMonteCarlo** is a programming interface to run identical simulations using
different Monte Carlo programs. The interface was designed to have common input
and output that are independent of any Monte Carlo code. This allows users to
combine the advantages of different codes and to compare the effect of different
physical models without manually creating and running new simulations for each
Monte Carlo program. The analysis of the results is also simplified by the
common output format where results are expressed in the same units.

**pyMonteCarlo** is currently under development.

Programs
--------

Bindings with the following Monte Carlo programs are currently available:

* DTSA-II/NISTMonte Gemini :cite:`ritchie2005`
* MONACO 3.0 :cite:`ammann1990`
* PENELOPE 2011 :cite:`salvat2011`
* Wincasino 2.48 :cite:`drouin2007`
* WinXRay 1.4 :cite:`gauvin2006`

The interface is, however, extendable to integrate other Monte Carlo programs,
including personal or protected codes.
See :ref:`newprogram` in the development section for more information.

pyMonteCarlo is written in Python, a cross-platform object-oriented programming
language.
It is licensed under the GNU GPL v3.

Authors
-------

- `Philippe T. Pinard <https://github.com/ppinard>`_ (High Wycombe, United Kingdom)
- `Hendrix Demers <https://github.com/drix00>`_ (McGill University, Montreal, Canada)
- `Raynald Gauvin <http://www.memrg.com>`_ (McGill University, Montreal, Canada)
- `Silvia Richter <https://github.com/silrichter>`_ (`RWTH Aachen University <http://www.gfe.rwth-aachen.de/seiteninhalte_english/esma.htm>`_, Aachen, Germany)

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   features
   documentation
   examples
   collaboration
   download
   appendices

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. bibliography::
