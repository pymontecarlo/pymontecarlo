
# ![Logo](https://raw.githubusercontent.com/pymontecarlo/pymontecarlo/master/logo/logo_64x64.png) pyMonteCarlo

[![PyPI](https://img.shields.io/pypi/v/pymontecarlo)](https://pypi.org/project/pyMonteCarlo)

**pyMonteCarlo** is a programming interface to run identical simulations using
different Monte Carlo programs. The interface was designed to have common input
and output that are independent of any Monte Carlo code. This allows users to
combine the advantages of different codes and to compare the effect of different
physical models without manually creating and running new simulations for each
Monte Carlo program. The analysis of the results is also simplified by the
common output format where results are expressed in the same units.

**pyMonteCarlo** is currently under development.

## Documentation

The [documentation](http://pymontecarlo.readthedocs.io) contains the
installation instructions, tutorials, supported Monte Carlo programs and API.

## License

**pyMonteCarlo** is licensed under Apache Software License 2.0.

## Citation

Pinard, P., Demers, H., Gauvin, R., & Richter, S. (2013). pyMonteCarlo: A Common Programming Interface for Running Identical Simulations using Different Monte Carlo Programs. Microscopy and Microanalysis, 19(S2), 822-823. doi:[10.1017/S1431927613006107](http://dx.doi.org/10.1017/S1431927613006107)

```bibtex
@article{pinard2013,
    author={Pinard, P.T. and Demers, H. and Gauvin, R. and Richter, S.},
    title={pyMonteCarlo: A Common Programming Interface for Running Identical Simulations using Different Monte Carlo Programs},
    journal={Microscopy and Microanalysis},
    volume={19},
    number={S2},
    publisher={Cambridge University Press},
    year={2013},
    pages={822–823},
    DOI={10.1017/S1431927613006107}
}
```

## Build status

Package | CI build | Code coverage
--- | --- | ---
pymontecarlo | [![CI](https://github.com/pymontecarlo/pymontecarlo/actions/workflows/ci.yml/badge.svg)](https://github.com/pymontecarlo/pymontecarlo/actions) | [![Codecov](https://img.shields.io/codecov/c/github/pymontecarlo/pymontecarlo)](https://codecov.io/gh/pymontecarlo/pymontecarlo)
pymontecarlo-gui | [![CI](https://github.com/pymontecarlo/pymontecarlo-gui/actions/workflows/ci.yml/badge.svg)](https://github.com/pymontecarlo/pymontecarlo-gui/actions) | [![Codecov](https://img.shields.io/codecov/c/github/pymontecarlo/pymontecarlo-gui)](https://codecov.io/gh/pymontecarlo/pymontecarlo-gui)
pymontecarlo-casino2 | [![CI](https://github.com/pymontecarlo/pymontecarlo-casino2/actions/workflows/ci.yml/badge.svg)](https://github.com/pymontecarlo/pymontecarlo-casino2/actions) | [![Codecov](https://img.shields.io/codecov/c/github/pymontecarlo/pymontecarlo-casino2)](https://codecov.io/gh/pymontecarlo/pymontecarlo-casino2)
pymontecarlo-penepma | [![CI](https://github.com/pymontecarlo/pymontecarlo-penepma/actions/workflows/ci.yml/badge.svg)](https://github.com/pymontecarlo/pymontecarlo-penepma/actions) | [![Codecov](https://img.shields.io/codecov/c/github/pymontecarlo/pymontecarlo-penepma)](https://codecov.io/gh/pymontecarlo/pymontecarlo-penepma)
pypenelopetools | [![CI](https://github.com/pymontecarlo/pypenelopetools/actions/workflows/ci.yml/badge.svg)](https://github.com/pymontecarlo/pypenelopetools/actions) | [![Codecov](https://img.shields.io/codecov/c/github/pymontecarlo/pypenelopetools)](https://codecov.io/gh/pymontecarlo/pypenelopetools)

## Contributors

- [Philippe T. Pinard](https://github.com/ppinard) (London, United Kingdom)
- [Hendrix Demers](https://github.com/drix00) (Montreal, Canada)
- [Raynald Gauvin](http://www.memrg.com) (McGill University, Montreal, Canada)
- [Silvia Richter](https://github.com/silrichter) ([RWTH Aachen University](http://www.gfe.rwth-aachen.de/seiteninhalte_english/esma.htm), Aachen, Germany)

<img src="https://upload.wikimedia.org/wikipedia/commons/1/1e/RWTH_Logo_3.svg" height="70">
<img src="https://upload.wikimedia.org/wikipedia/commons/e/e4/McGill_Athletics_wordmark.png" height="40">

## Release notes

### 1.1.0

- Fix issues with newer releases of dependencies

## Copyrights

Copyright (c) 2011 - 2016/06, Silvia Richter and Philippe Pinard

Copyright (c) 2016/06 - , Philippe Pinard
