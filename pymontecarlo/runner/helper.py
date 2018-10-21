""""""

# Standard library modules.
import multiprocessing

# Third party modules.
import progressbar

# Local modules.
from pymontecarlo.runner.local import LocalSimulationRunner

# Globals and constants variables.

def run(list_options, project=None, max_workers=None, runner_class=None, progress=None):
    """
    Helper function to run simulations.
    The function returns a :class:`Project <pymontecarlo.project.Project>` 
    containing the simulations after they all have been simulated.
    
    :param list_options: List of options to simulate.
    
    :param project: project where to save the simulations. 
        If ``None``, a new project is created.
    :type project: :class:`Project <pymontecarlo.project.Project>`
    
    :param max_workers: number of worker/CPU to use.
        If ``None``, the number of CPUs on the computer will be used.
    :type max_workers: :class:`int`
    
    :param runner_class: runner class to use.
        If ``None``, the default is :class:`LocalSimulationRunner <pymontecarlo.runner.local.LocalSimulationRunner>`
    
    :param progress: an instance of a progressbar2 object
        If ``None``, a progressbar2 object is created.
        
    :return: project
    :rtype: :class:`Project <pymontecarlo.project.Project>`
    """
    if max_workers is None:
        max_workers = multiprocessing.cpu_count()
    if runner_class is None:
        runner_class = LocalSimulationRunner
    if progress is None:
        progress = progressbar.ProgressBar()

    with runner_class(max_workers=max_workers) as runner:
        runner.submit(*list_options)
        progress.start(max_value=1.0)

        while not runner.wait(1):
            progress.update(runner.progress)

        for future in runner.failed_futures:
            print(future.exception())

        print('{} simulations succeeded, {} failed'.format(runner.done_count,
                                                           runner.failed_count))

        runner.project.recalculate()

        return runner.project
