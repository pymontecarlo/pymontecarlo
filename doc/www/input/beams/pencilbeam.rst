
.. _pencilbeam:

Pencil beam
###########

A pencil beam is a one dimensional beam (no width).
Under normal conditions, pyMonteCarlo assumes that the particles inside the
beam are travelling along the negative z direction from a location above the 
sample.
By default, the sample surface is located on the XY place (z = 0).
Some Monte Carlo programs allow to define an aperture angle. 
It is defined as 

Availability
^^^^^^^^^^^^

.. availability:: BEAMS
   :only: pymontecarlo.input.beam.PencilBeam
   
.. note::

   In PENEPMA and PENSHOWER, a :ref:`Gaussian beam <gaussianbeam>` with a 
   beam diameter of 0 m can be used instead.

API
^^^

.. module:: pymontecarlo.input.beam

.. autoclass:: PencilBeam
   :members: