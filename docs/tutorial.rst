.. _tutorial:

========
Tutorial
========

A (Monte Carlo) :class:`Simulation <pymontecarlo.simulation.Simulation>` 
consists in (1) options, defining all the necessary parameters to setup the 
simulation, and (2) results, containing all the outputs of a simulation.
One or more simulations form a :class:`Project <pymontecarlo.project.Project>`.
A **pyMonteCarlo** project stored on disk has the extension `.mcsim`.
It consists of a `HDF5 <http://hdf5group.org>`_ file and can be opened in the
`HDFViewer <http://hdf5group.org>`_ or using any HDF5 library.

Options
=======

Going back to the first component of a 
:class:`Simulation <pymontecarlo.simulation.Simulation>`, the options.
The options are defined by the class 
:class:`Options <pymontecarlo.options.options.Options>`.
It contains all the parameters necessary to run a simulation.
The parameters are grouped into four categories: program, beam, sample and analyses.

Program
-------

The program is specific to a particular Monte Carlo program.
Each program follows the contract specified by the base program class
:class:`Program <pymontecarlo.options.program.base.Program>`.
One implementation is for :ref:`Casino 2 <supported-monte-carlo-programs-casino2>`
as part of the package **pymontecarlo-casino2**. 
The program can be imported as follow::

    from pymontecarlo_casino2.program import Casino2Program
    
The parameters associated with the program will depend on each Monte Carlo program.
For Casino 2, the number of trajectories and the models used for the simulation
can be specified.
Here is an example with the default models and 5000 trajectories::

    program = Casino2Program(5000)
    
Throughout **pyMonteCarlo**, a parameter can also be set/modified using its
attribute inside the class::

    program.number_trajectories = 6000
    
All parameters are completely mutable and are only validated before a 
simulation starts.

Beam
----

The second category of parameters is the beam.
At the moment, two types of beam are implemented/supported: a Gaussian
(:class:`GaussianBeam <pymontecarlo.options.beam.gaussian.GaussianBeam>`) and a
cylindrical beam (:class:`CylindricalBeam <pymontecarlo.options.beam.cylindrical.CylindricalBeam>`).
All beam implementations must define the energy and type of the incident particles
as defined by the base beam class :class:`Beam <pymontecarlo.options.beam.base.Beam>`.
The type of incident particle is defined for future expansions, since all 
currently supported Monte Carlo programs only accept 
:attr:`ELECTRON <pymontecarlo.options.particle.Particle.ELECTRON>`.
Unless otherwise stated, all beams assume that the incident particles travel
downwards along the z-axis, i.e. following the vector ``(0, 0, -1)``.

.. note:: 

   See the **supported options** section for each Monte Carlo program on the
   :ref:`supported-monte-carlo-programs` page for more details.

The Gaussian beam is the most supported by the different Monte Carlo programs.
Besides the incident energy, the diameter corresponding to the full width at 
half maximum (FWHM) of a two dimensional Gaussian distribution must be specified.
For a 15kV beam with a diameter of 10nm::

    from pymontecarlo.options.beam.gaussian import GaussianBeam
    beam = GaussianBeam(15e3, 10e-9)

Other parameters of the beam are the beam center position. 
The actual position of each particle will be randomly sampled by the Monte Carlo
program to obtain a two dimensional Gaussian distribution centered at the
specified position.
By default, the beam is centered at ``x = 0m`` and ``y = 0m``.
The position can be changed using either attribute::

    beam.x_m = 100e-9
    beam.y_m = 200e-9
    
If you are looking to perform a line scan, you should have a look at the
Gaussian beam builder class 
:class:`GaussianBeamBuilder <pymontecarlo.options.beam.gaussian.GaussianBeamBuilder>`.
Builder classes are helper classes to create multiple instances by varying one 
or more parameters.
For example, if we would like to create a Gaussian beam at two incident energy
(5 and 15kV) and scan the sample from -100 to 100μm with a step size of 25μm::

    from pymontecarlo.options.beam.gaussian import GaussianBeamBuilder
    builder = GaussianBeamBuilder()
    builder.add_energy_eV(5e3)
    builder.add_energy_keV(15)
    builder.add_diameter_m(10e-9)
    builder.add_linescan_x(-100e-6, 100e-6, 25e-6)
    beams = builder.build()
    
The variable :obj:`beams` is a :class:`list` of 16 Gaussian beams, 2 incident
electron energies and 8 positions in the linescan.
Note however that each :class:`Options <pymontecarlo.options.options.Options>`
instance can only take one beam. 
This will result in an *exception* at validation::

    options.beam = beams # Incorrect

Sample
------

The sample parameter defines the geometry and the materials of the sample 
being bombarded by the incident particles.
There are currently 5 types of sample implemented:

    * substrate (:class:`SubstrateSample <pymontecarlo.options.sample.substrate.SubstrateSample>`):
      An infinitely thick sample. 
    * inclusion (:class:`InclusionSample <pymontecarlo.options.sample.inclusion.InclusionSample>`):
      An half-sphere inclusion in a substrate.
    * horizontal layered (:class:`HorizontalLayerSample <pymontecarlo.options.sample.horizontallayers.HorizontalLayerSample>`):
      Creates a multi-layers geometry.
      The layers are assumed to be in the x-y plane (normal parallel to z) at
      tilt of 0.0°.
    * vertical layered (:class:`VericalLayerSample <pymontecarlo.options.sample.verticallayers.VericalLayerSample>`):
      Creates a grain boundaries sample.
      It consists of 0 or many layers in the y-z plane (normal parallel to x)
      simulating interfaces between different materials.
      If no layer is defined, the geometry is a couple.
    * sphere (:class:`SphereSample <pymontecarlo.options.sample.sphere.SphereSample>`):
      A sphere in vacuum.
    
For all types of sample, the sample is entirely located below the ``z = 0`` plane.
While some Monte Carlo programs support custom and complex sample definitions,
it was chosen for simplicity and compatibility to constrain the available types
of sample.
If you would like to suggest/contribute another type of sample, please open an
enhancement `issue <https://github.com/pymontecarlo/pymontecarlo/issues>`_ or 
submit a `pull request <https://github.com/pymontecarlo/pymontecarlo/pulls>`_.

Before creating a sample, material(s) must be defined.
A material defines the composition and density in a part of the sample 
(e.g. layer or substrate).
After importing the :class:`Material <pymontecarlo.options.material.Material>` 
class::

    from pymontecarlo.options.material import Material

There are three ways to create a material:

    1. Pure, single element material::
       
        material = Material.pure(14) # pure silicon
       
    2. A chemical formula::
    
        material = Material.from_formula('SiO2')
        
    3. Composition in mass fraction. 
       The composition is expressed as a :class:`dict` where keys are atomic 
       numbers and values, mass fractions::
    
        composition = {29: 0.4, 30: 0.6}
        material = Material('Brass', composition)
       
In all three cases the mass density (in kg/m3) can be specified as an argument
or set from its attribute::

    material.density_kg_per_m3 = 8400
    material.density_g_per_cm3 = 8.4
    
If the density is not specified, it is calculated using this following formula:

.. math:: 

   \frac{1}{\rho} = \sum{\frac{m_i}{\rho_i}}

where :math:`\rho_i` and :math:`m_i` are respectively the elemental mass density 
and mass fraction of element *i*.
 