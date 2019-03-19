# hepdata_lib

[![DOI](https://zenodo.org/badge/129248575.svg)](https://zenodo.org/badge/latestdoi/129248575)
[![PyPI version](https://badge.fury.io/py/hepdata-lib.svg)](https://badge.fury.io/py/hepdata-lib)
[![Build Status](https://travis-ci.org/HEPData/hepdata_lib.svg?branch=master)](https://travis-ci.org/HEPData/hepdata_lib)
[![Coverage Status](https://coveralls.io/repos/github/HEPData/hepdata_lib/badge.svg?branch=master)](https://coveralls.io/github/HEPData/hepdata_lib?branch=master)
[![Documentation Status](https://readthedocs.org/projects/hepdata-lib/badge/)](http://hepdata-lib.readthedocs.io/)
[![Docker Hub](https://images.microbadger.com/badges/image/clelange/hepdata_lib.svg)](https://hub.docker.com/r/clelange/hepdata_lib/)

Library for getting your data into HEPData

## Installation

```shell
pip install hepdata_lib
```

## Getting started

For using `hepdata_lib`, you don't even need to install it, but can use the [binder](https://mybinder.org/) or [SWAN](https://swan.cern.ch/) (CERN-only) services using one of the buttons below and following the instructions in the notebook with name [Getting_started](examples/Getting_started.ipynb):

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/HEPData/hepdata_lib/master?filepath=examples/Getting_started.ipynb)
[![SWAN](https://swanserver.web.cern.ch/swanserver/images/badge_swan_white_150.png)](https://cern.ch/swanserver/cgi-bin/go?projurl=https://github.com/HEPData/hepdata_lib.git)

You can also use the docker image:

```shell
docker run --rm -it -p 8888:8888 clelange/hepdata_lib
```

And then point your browser to [http://localhost:8888](http://localhost:8888) and use the token that is printed out.

## Further examples

There are a few more examples available that can directly be run using the [binder](https://mybinder.org/) links below or using [SWAN](https://swan.cern.ch/) (CERN-only, please use LCG release LCG_94 or later) and selecting the corresponding notebook manually:

- [Reading in text files](examples/Getting_started.ipynb) [![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/HEPData/hepdata_lib/master?filepath=examples/Getting_started.ipynb)
- [Reading in a CMS combine ntuple](examples/combine_limits.ipynb) [![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/HEPData/hepdata_lib/master?filepath=examples/combine_limits.ipynb)
- [Reading in ROOT histograms](examples/reading_histograms.ipynb) [![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/HEPData/hepdata_lib/master?filepath=examples/reading_histograms.ipynb)

## External dependencies

- [ROOT](https://root.cern.ch)
- [ImageMagick](https://www.imagemagick.org)

Make sure that you have `ROOT` in your `$PYTHONPATH` and that the `convert` command is available by adding its location to your `$PATH` if needed.
