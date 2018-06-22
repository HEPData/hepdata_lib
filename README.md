# hepdata_lib

[![DOI](https://zenodo.org/badge/129248575.svg)](https://zenodo.org/badge/latestdoi/129248575)
[![PyPI version](https://badge.fury.io/py/hepdata_lib.svg)](https://badge.fury.io/py/hepdata_lib)
[![Build Status](https://travis-ci.org/clelange/hepdata_lib.svg?branch=master)](https://travis-ci.org/clelange/hepdata_lib)
[![Documentation Status](https://readthedocs.org/projects/hepdata-lib/badge/)](http://hepdata-lib.readthedocs.io/)

Library for getting your data into HEPData

## Installation

```
pip install hepdata_lib
```

## Getting started

For using `hepdata_lib`, you don't even need to install it, but can use the [binder](https://mybinder.org/) or [SWAN](https://swan.cern.ch/) (CERN-only) services using one of the buttons below and following the instructions in the notebook with name [Getting_started](notebooks/Getting_started.ipynb):

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/clelange/hepdata_lib/master?filepath=notebooks/Getting_started.ipynb)
[![SWAN](https://swanserver.web.cern.ch/swanserver/images/badge_swan_white_150.png)](https://cern.ch/swanserver/cgi-bin/go?projurl=https://mybinder.org/v2/gh/clelange/hepdata_lib.git)

## Further examples

There are a few more examples available that can directly be run using the [binder](https://mybinder.org/) links below or using [SWAN](https://swan.cern.ch/) (CERN-only) and selecting the corresponding notebook manually:

- [Reading in a CMS combine ntuple](notebooks/combine_limits.ipynb) [![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/clelange/hepdata_lib/master?filepath=notebooks/combine_limits.ipynb)

## External dependencies

- [ROOT](https://root.cern.ch)
- [ImageMagick](https://www.imagemagick.org)

Make sure that you have `ROOT` in your `$PYTHONPATH` and that the `convert` command is available by adding its location to your `$PATH` if needed.
