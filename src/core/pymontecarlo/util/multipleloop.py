#!/usr/bin/env python
"""
================================================================================
:mod:`multipleloop` -- Utilities to loop over values
================================================================================

.. module:: multipleloop
   :synopsis: Utilities to loop over values

.. inheritance-diagram:: multipleloop

This module provides a tool for handling computer experiments with
of a set of input parameters, where each input parameter
is varied in a prescribed fashion.

In short, the parameters are held in a dictionary where the keys are
the names of the parameters and the values are the numerical, string
or other values of the parameters.  The value can take on multiple
values: e.g., an integer parameter 'a' can have values -1, 1 and
10. Similarly, a string parameter 'method' can have values 'Newton'
and 'Bisection'. The module will generate all combination of all
parameters and values, which in the mentioned example will be
(-1, 'Newton'), (1, 'Newton'), (10, 'Newton'), (-1, 'Bisection'),
(1, 'Bisection'), and (10, 'Bisection'). Particular combination
of values can easily be removed.

The usage and implementation of the module are documented in the
book "Python Scripting for Computational Science" (H. P. Langtangen,
Springer, 2009), Chapter 12.1.


Simple use of basic functionality in the module are shown below.
See the book for explanations and more comprehensive examples.

>>> from scitools.multipleloop import *
>>>
>>> # parameter names and multiple values,
>>> # using the special multipleloop syntax:
>>> p = {'A': '1 & 2 & 5', 'B': 'hello & world'}
>>>
>>> # turn multiple values syntax like 1 & 2 & 5 into list of values
>>> input2values(p['A'])
[1, 2, 5]
>>>
>>> prm_values = [(name, input2values(p[name])) for name in p]
>>> import pprint
>>> pprint.pprint(prm_values)
[('A', [1, 2, 5]), ('B', ['hello', 'world'])]
>>>
>>> # main function:
>>> all, names, varied = combine(prm_values)
>>>
>>> # all[i] holds all parameter values in experiment no i,
>>> # names holds the parameter names, and varied holds the
>>> # parameter names that are actually varied (not fixed values)
>>> print names
['A', 'B']
>>> print varied
['A', 'B']
>>> pprint.pprint(all)
[[1, 'hello'],
 [2, 'hello'],
 [5, 'hello'],
 [1, 'world'],
 [2, 'world'],
 [5, 'world']]
>>>
>>> e = 1
>>> for experiment in all:
...     print 'Experiment %4d:' % e,
...     for name, value in zip(names, experiment):
...         print '%s: %s' % (name, value),
...     print # newline
...     e += 1  # experiment counter
...
Experiment    1: A: 1 B: hello
Experiment    2: A: 2 B: hello
Experiment    3: A: 5 B: hello
Experiment    4: A: 1 B: world
Experiment    5: A: 2 B: world
Experiment    6: A: 5 B: world
>>>
>>> # turn parameter names and values into command-line options
>>> # (useful for running a program that takes parameter names prefixed
>>> # by - or -- as command-line options):
>>> cmd = options(all, names, prefix='-')
>>> for c in cmd:
...     print c
...     #commands.getstatusoutput(programname + ' ' + c)
...
-A True -B 'hello'
-A True -B 'hello'
-A True -B 'hello'
-A True -B 'world'
-A True -B 'world'
-A True -B 'world'
>>>
>>> print 'all combinations: %d' % len(all)
all combinations: 6
>>>
>>> # compute pairs:
>>> all = pairs(prm_values)
>>> print 'all pairs: %d' % len(all); pprint.pprint(all)
all pairs: 6
[[1, 'hello'],
 [2, 'hello'],
 [5, 'hello'],
 [5, 'world'],
 [2, 'world'],
 [1, 'world']]
>>>
>>> # alternative class interface:
>>> experiments = MultipleLoop(option_prefix='-')
>>> for name in p:
...     experiments.register_parameter(name, p[name])
...
>>> experiments.combine()  # compute all combinations
>>>
>>> # remove all experiments corresponding to a condition:
>>> nremoved = experiments.remove('A == 5')
>>>
>>> # look at the attributes of this instance:
>>> pprint.pprint(experiments.all)
[[1, 'hello'], [2, 'hello'], [1, 'world'], [2, 'world']]
>>> print experiments.names
['A', 'B']
>>> print experiments.varied
['A', 'B']
>>> print experiments.options
["-A True -B 'hello'", "-A True -B 'hello'", "-A True -B 'world'",
 "-A True -B 'world'"]
>>> pprint.pprint(experiments.prm_values)
[('A', [1, 2, 5]), ('B', ['hello', 'world'])]

Here is another example with more experiments::

>>> p = {'b': '1 & 0 & 0.5', 'func': 'y & siny', 'w': '[1:1.3,0.1]'}
>>> prm_values = [(name, input2values(p[name])) for name in p]
>>> import pprint
>>> pprint.pprint(prm_values)
[('b', [1, 0, 0.5]),
 ('w', [1, 1.1000000000000001, 1.2000000000000002]),
 ('func', ['y', 'siny'])]
>>>
>>> # main function:
>>> all, names, varied = combine(prm_values)
>>>
>>> print names
['b', 'w', 'func']
>>> print varied
['b', 'w', 'func']
>>> pprint.pprint(all)
[[1, 1, 'y'],
 [0, 1, 'y'],
 [0.5, 1, 'y'],
 [1, 1.1000000000000001, 'y'],
 [0, 1.1000000000000001, 'y'],
 [0.5, 1.1000000000000001, 'y'],
 [1, 1.2000000000000002, 'y'],
 [0, 1.2000000000000002, 'y'],
 [0.5, 1.2000000000000002, 'y'],
 [1, 1, 'siny'],
 [0, 1, 'siny'],
 [0.5, 1, 'siny'],
 [1, 1.1000000000000001, 'siny'],
 [0, 1.1000000000000001, 'siny'],
 [0.5, 1.1000000000000001, 'siny'],
 [1, 1.2000000000000002, 'siny'],
 [0, 1.2000000000000002, 'siny'],
 [0.5, 1.2000000000000002, 'siny']]
>>>
>>> print 'all combinations: %d' % len(all)
all combinations: 18
>>>
>>> # compute pairs:
>>> all = pairs(prm_values)
>>> print 'all pairs: %d' % len(all); pprint.pprint(all)
all pairs: 9
[[1, 1, 'y'],
 [0, 1.1000000000000001, 'y'],
 [0.5, 1.2000000000000002, 'y'],
 [0.5, 1.1000000000000001, 'siny'],
 [0, 1, 'siny'],
 [1, 1.2000000000000002, 'siny'],
 [1, 1.1000000000000001, 'siny'],
 [0, 1.2000000000000002, 'siny'],
 [0.5, 1, 'siny']]
>>>
>>> # alternative class interface:
>>> experiments = MultipleLoop(option_prefix='-')
>>> for name in p:
...     experiments.register_parameter(name, p[name])
...
>>> experiments.combine()
>>>
>>> # remove all experiments corresponding to a condition:
>>> nremoved = experiments.remove('b == 1')
>>>
>>> # look at the attributes of this instance:
>>> pprint.pprint(experiments.all)
[[0, 1, 'y'],
 [0.5, 1, 'y'],
 [0, 1.1000000000000001, 'y'],
 [0.5, 1.1000000000000001, 'y'],
 [0, 1.2000000000000002, 'y'],
 [0.5, 1.2000000000000002, 'y'],
 [0, 1, 'siny'],
 [0.5, 1, 'siny'],
 [0, 1.1000000000000001, 'siny'],
 [0.5, 1.1000000000000001, 'siny'],
 [0, 1.2000000000000002, 'siny'],
 [0.5, 1.2000000000000002, 'siny']]

>>> # explore the response of varied parameters:
>>> # function = []  # list of (response, (param1, param2, ...))
>>> # the (param1, param2, ...) list equals the varied parameter values
>>> # in each experiment (varied_parameters in the loop below)
>>>
>>> for cmlargs, parameters, varied_parameters in experiments:
...     args = ', '.join(['%s=%s' % (name,value) for name, value in zip(experiments.names, parameters)])
...     print
...     print 'can call some function:'
...     print 'response = myfunc(%s)' % args
...     print 'or run some program with options:'
...     print 'prompt> myprog ', cmlargs
...     print 'and extract a response from the program output'
...     print 'function.append((response, varied_parameters))'
...

"""

# Script information for the file.
__author__ = "scitools"
__version__ = "0.9.0"
__license__ = "New BSD"
__url__ = "http://code.google.com/p/scitools/"

# Standard library modules.

# Third party modules.

# Local modules.

# Globals and constants variables.

def _outer(a, b):
    """
    Return the outer product/combination of two lists.
    a is a multi- or one-dimensional list,
    b is a one-dimensional list, tuple, NumPy array or scalar (new parameter)
    Return:  outer combination 'all'.

    The function is to be called repeatedly::

        all = _outer(all, p)
    """
    all_ = []
    if not isinstance(a, list):
        raise TypeError('a must be a list')
    if isinstance(b, (float, int, complex, str)):  b = [b] # scalar?

    if len(a) == 0:
        # first call:
        for j in b:
            all_.append([j])
    else:
        for j in b:
            for i in a:
                if not isinstance(i, list):
                    raise TypeError('a must be list of list')
                # note: i refers to a list; i.append(j) changes
                # the underlying list (in a), which is not what
                # we want, we need a copy, extend the copy, and
                # add to all
                k = i + [j] # extend previous prms with new one
                all_.append(k)
    return all_

def combine(prm_values):
    """
    Compute the combination of all parameter values in the prm_values
    (nested) list. Main function in this module.

    param prm_values: nested list ``(parameter_name, list_of_parameter_values)``
    or dictionary ``prm_values[parameter_name] = list_of_parameter_values``.
    return: (all, names, varied) where

      - all contains all combinations (experiments)
        all[i] is the list of individual parameter values in
        experiment no i

      - names contains a list of all parameter names

      - varied holds a list of parameter names that are varied
        (i.e. where there is more than one value of the parameter,
        the rest of the parameters have fixed values)


    Code example:

    >>> dx = array([1.0/2**k for k in range(2,5)])
    >>> dt = 3*dx;  dt = dt[:-1]
    >>> p = {'dx': dx, 'dt': dt}
    >>> p
    {'dt': [ 0.75 , 0.375,], 'dx': [ 0.25  , 0.125 , 0.0625,]}
    >>> all, names, varied = combine(p)
    >>> all
    [[0.75, 0.25], [0.375, 0.25], [0.75, 0.125], [0.375, 0.125],
     [0.75, 0.0625], [0.375, 0.0625]]
    """
    if isinstance(prm_values, dict):
        # turn dict into list [(name,values),(name,values),...]:
        prm_values = [(name, prm_values[name]) \
                      for name in prm_values]
    all_ = []
    varied = []
    for name, values in prm_values:
        all_ = _outer(all_, values)
        if isinstance(values, list) and len(values) > 1:
            varied.append(name)
    names = [name for name, values in prm_values]
    return all_, names, varied

