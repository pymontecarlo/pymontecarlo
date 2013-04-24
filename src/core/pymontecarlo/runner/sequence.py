#!/usr/bin/env python
"""
================================================================================
:mod:`sequence` -- Adaptor to run sequences.
================================================================================

.. module:: sequence
   :synopsis: Runner to run sequences.

.. inheritance-diagram:: pymontecarlo.runner.sequence

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import uuid

# Third party modules.

# Local modules.
from pymontecarlo.runner.base import _Runner
from pymontecarlo.output.results import ResultsSequence

# Globals and constants variables.

class SequenceRunner(_Runner):

    def __init__(self, runner):
        _Runner.__init__(self, runner.program)
        self._runner = runner
        self._lookup = {}
        
    def put(self, options_seq):
        options_seq_id = uuid.uuid4()
        for pos, options in enumerate(options_seq):
            self._lookup[options.uuid] = (options_seq_id, pos)        
            self._runner.put(options)

    def start(self):
        self._runner.start()

    def stop(self):
        self._runner.stop()

    def close(self):
        self._runner.close()

    def is_alive(self):
        return self._runner.is_alive()

    def join(self):
        self._runner.join()

    def get_results(self):
        list_results_seq = []
        list_all_results = self._runner.get_results()
        
        # Create dictionary where results are sorted by sequence id
        dict_results = {}
        for results in list_all_results:
            options_seq_id = self._lookup[results.options.uuid][0]
            if not options_seq_id in dict_results:
                dict_results[options_seq_id] = {}
            else:
                dict_results[options_seq_id].append(results)
        
        # Create ResultsSequence objects by sorting the lists in the dictionary
        for list_results in dict_results:
            pos = lambda x: self._lookup[x.options.uuid][1]
            list_results = sorted(list_results, key=pos)
            list_results_seq.append(ResultsSequence(list_results))
        
        # Delete all used options from the lookup
        for results in list_all_results:
            del self._lookup[results.options.uuid]
                
        return list_results_seq
    
    def report(self):
        return self._runner.report()

