# hepdata_lib

[![DOI](https://zenodo.org/badge/129248575.svg)](https://zenodo.org/badge/latestdoi/129248575)
[![PyPI version](https://badge.fury.io/py/hepdata-lib.svg)](https://badge.fury.io/py/hepdata-lib)
[![Actions Status](https://github.com/HEPData/hepdata_lib/workflows/tests/badge.svg)](https://github.com/HEPData/hepdata_lib/actions)
[![Coverage Status](https://coveralls.io/repos/github/SirVheod/hepdata_lib/badge.svg?branch=master)](https://coveralls.io/github/SirVheod/hepdata_lib?branch=master)
[![Documentation Status](https://readthedocs.org/projects/hepdata-lib/badge/)](http://hepdata-lib.readthedocs.io/)
[![Docker Hub](https://images.microbadger.com/badges/image/clelange/hepdata_lib.svg)](https://hub.docker.com/r/clelange/hepdata_lib/)

Library for getting your data into HEPData

## Installation

It is highly recommended you install `hepdata_lib` into a [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/).

```shell
pip install hepdata_lib
```

If you are not sure about your Python environment, please also see below how to use `hepdata_lib` in a Docker or Singularity container.

## Getting started

For using `hepdata_lib`, you don't even need to install it, but can use the [binder](https://mybinder.org/) or [SWAN](https://swan.cern.ch/) (CERN-only) services using one of the buttons below and following the instructions in the notebook with name [Getting_started](examples/Getting_started.ipynb):

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/HEPData/hepdata_lib/master?filepath=examples/Getting_started.ipynb)
[![SWAN](https://swanserver.web.cern.ch/swanserver/images/badge_swan_white_150.png)](https://cern.ch/swanserver/cgi-bin/go/?projurl=https://github.com/HEPData/hepdata_lib.git)

You can also use the Docker image:

```shell
docker run --rm -it -p 8888:8888 -v ${PWD}:/home/hepdata clelange/hepdata_lib
```

And then point your browser to [http://localhost:8888](http://localhost:8888) and use the token that is printed out. The output will end up in your current working directory (`${PWD}`).

If you prefer a shell, instead run:

```shell
docker run --rm -it -p 8888:8888 -v ${PWD}:/home/hepdata clelange/hepdata_lib bash
```

If on CERN LXPLUS or anywhere else where there is Singularity available but not Docker, you can still use the docker image:

```shell
export SINGULARITY_CACHEDIR="/tmp/$(whoami)/singularity"
singularity shell -B /afs -B /eos docker://clelange/hepdata_lib bash
```

Unpacking the image can take a few minutes the first time you use it. Please be patient. Both EOS and AFS should be available and the output will be in your current working directory.

## Further examples

There are a few more examples available that can directly be run using the [binder](https://mybinder.org/) links below or using [SWAN](https://swan.cern.ch/) (CERN-only, please use LCG release LCG_94 or later) and selecting the corresponding notebook manually:

- [Reading in text files](examples/Getting_started.ipynb) [![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/HEPData/hepdata_lib/master?filepath=examples/Getting_started.ipynb)
- [Reading in a CMS combine ntuple](examples/combine_limits.ipynb) [![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/HEPData/hepdata_lib/master?filepath=examples/combine_limits.ipynb)
- [Reading in ROOT histograms](examples/reading_histograms.ipynb) [![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/HEPData/hepdata_lib/master?filepath=examples/reading_histograms.ipynb)
- [Reading a correlation matrix](examples/correlation.ipynb) [![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/HEPData/hepdata_lib/master?filepath=examples/correlation.ipynb)
- [Reading TGraph and TGraphError from '.C' files](examples/read_c_file.ipynb) [![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/HEPData/hepdata_lib/master?filepath=examples/read_c_file.ipynb)

## External dependencies

- [ROOT](https://root.cern.ch)
- [ImageMagick](https://www.imagemagick.org)

Make sure that you have `ROOT` in your `$PYTHONPATH` and that the `convert` command is available by adding its location to your `$PATH` if needed.
