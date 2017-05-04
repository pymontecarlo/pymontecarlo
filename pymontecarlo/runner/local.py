"""
Local runner.
"""

# Standard library modules.
import os
import tempfile
import shutil

# Third party modules.

# Local modules.
from pymontecarlo.runner.base import SimulationRunner

# Globals and constants variables.

class LocalSimulationRunner(SimulationRunner):

    def _prepare_target(self):
        # Create output directory
        if self.project.filepath is not None:
            head, tail = os.path.split(self.project.filepath)
            simsdirname = os.path.splitext(tail)[0] + '_simulations'
            simdir = os.path.join(head, simsdirname)
            temporary = False
        else:
            temporary = True

        # Run function
        def target(token, simulation):
            program = simulation.options.program
            worker = program.create_worker()

            if temporary:
                outputdir = tempfile.mkdtemp()
            else:
                outputdir = os.path.join(simdir, simulation.identifier)
            os.makedirs(outputdir, exist_ok=True)

            try:
                worker.run(token, simulation, outputdir)

            finally:
                if temporary:
                    shutil.rmtree(outputdir, ignore_errors=True)

            return simulation

        return target

