""""""

# Standard library modules.
import asyncio
import multiprocessing

# Third party modules.

# Local modules.
from pymontecarlo.runner.local import LocalSimulationRunner
from pymontecarlo.util.token import TqdmToken

# Globals and constants variables.


async def run_async(
    list_options, project=None, max_workers=None, runner_class=None, progress=True
):
    """
    Helper function to run simulations.
    The function returns a :class:`Project <pymontecarlo.project.Project>`
    containing the simulations after they all have been simulated.

    Args:
        list_options (list): List of options to simulate.

        project (:class:`Project <pymontecarlo.project.Project>`):
            project where to save the simulations.
            If ``None``, a new project is created.

        max_workers (int): number of worker/CPU to use.
            If ``None``, the number of CPUs on the computer will be used.

        runner_class: runner class to use.
            If ``None``, the default is :class:`LocalSimulationRunner <pymontecarlo.runner.local.LocalSimulationRunner>`

        progress (bool): whether to show a progress bar

    Returns:
        :class:`Project <pymontecarlo.project.Project>`: project
    """
    if max_workers is None:
        max_workers = multiprocessing.cpu_count()

    if runner_class is None:
        runner_class = LocalSimulationRunner

    if progress:
        token = TqdmToken("Simulations")
    else:
        token = None

    async with runner_class(
        project=project, token=token, max_workers=max_workers
    ) as runner:
        runner.token.start()

        await runner.submit(*list_options)
        await runner.shutdown()

        runner.token.done()
        return runner.project


def run(list_options, project=None, max_workers=None, runner_class=None, progress=True):
    return asyncio.run(
        run_async(list_options, project, max_workers, runner_class, progress)
    )
