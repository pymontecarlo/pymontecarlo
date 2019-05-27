===========================
|pymontecarlo| pyMonteCarlo
===========================

.. |pymontecarlo| image:: https://raw.githubusercontent.com/pymontecarlo/pymontecarlo/master/logo/logo_64x64.png
   :alt:

**pyMonteCarlo** is a programming interface to run identical simulations using different Monte Carlo programs.
The interface was designed to have common input and output that are independent of any Monte Carlo code.
This allows users to combine the advantages of different codes and to compare the effect of different physical models without manually creating and running new simulations for each Monte Carlo program.
The analysis of the results is also simplified by the common output format where results are expressed in the same units.

**pyMonteCarlo** is mainly designed and developed to fulfill simulation needs and solve problems faced by the electron microscopy and microanalysis community.
Adapting **pyMonteCarlo** to other scientific fields is not completely excluded, but it is a more long-term objective.

Goals
=====

**pyMonteCarlo** has the following goals:

    * Provide a common interface to setup Monte Carlo simulations for the electron microscopy and microanalysis community.
    * Provide a common interface to analyze and report results from simulations.
    * Easy way to create several simulations by varying one or more parameters.
    * Store results in a open, easy accessible file format.
    * Support several Monte Carlo programs.
    * Be extensible to new Monte Carlo programs.
    * Run on multiple operating systems, including on computer clusters.

Reversely, **pyMonteCarlo** does *not* attempt to:

    * Support all the finer details and particularities of each Monte Carlo program.
      **pyMonteCarlo** tries to be as general as possible.
      This allows the same simulation options to be simulated on several programs.
    * Provide new features to existing Monte Carlo program.
      Each program is taken as is.
      The development of new features is left to the original authors of the program.
    * Provide a complete suite of analysis tools.
      **pyMonteCarlo** provides general tools to tabulate and plot results.
      This cannot however fulfill the needs of all users.
      Results can be exported to *csv* and *Excel* file.
      Users can also write their own Python scripts to analyze their results.

License
=======

**pyMonteCarlo** and the packages providing interfaces to Monte Carlo programs are licensed under Apache Software License 2.0.

Contributors
============

- `Philippe T. Pinard <https://github.com/ppinard>`_ (High Wycombe, United Kingdom)
- `Hendrix Demers <https://github.com/drix00>`_ (Montreal, Canada)
- `Raynald Gauvin <http://www.memrg.com>`_ (McGill University, Montreal, Canada)
- `Silvia Richter <https://github.com/silrichter>`_ (`RWTH Aachen University <http://www.gfe.rwth-aachen.de/seiteninhalte_english/esma.htm>`_, Aachen, Germany)

.. toctree::
   :caption: Contents
   :maxdepth: 2

   installation
   tutorials
   supported-monte-carlo-programs
   supported-options
   examples
   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
