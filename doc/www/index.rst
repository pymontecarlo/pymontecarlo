Welcome
#######

.. toctree::
   :hidden:
   
   features
   documentation
   examples
   collaboration
   download

pyMonteCarlo is a programming interface to run identical simulations using
different Monte Carlo programs.
The interface was designed to have common input and output that are 
independent of any Monte Carlo code.
This allows users to combine the advantages of different codes and to compare
the effect of different physical models without manually creating and running
new simulations for each Monte Carlo program.
The analysis of the results is also simplified by the common output format
where results are expressed in the same units.

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
Binary version for Windows and Linux Debian are available to :doc:`download`.

Getting started
###############

* :doc:`input/beam`
* 

Authors
#######

* Philippe T. Pinard
* Hendrix Demers


.. bibliography::

