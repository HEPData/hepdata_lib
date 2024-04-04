# hepdata_lib

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1217998.svg)](https://doi.org/10.5281/zenodo.1217998)
[![PyPI version](https://badge.fury.io/py/hepdata-lib.svg)](https://badge.fury.io/py/hepdata-lib)
[![Actions Status](https://github.com/HEPData/hepdata_lib/workflows/tests/badge.svg)](https://github.com/HEPData/hepdata_lib/actions)
[![Coverage Status](https://codecov.io/gh/HEPData/hepdata_lib/graph/badge.svg?branch=main)](https://codecov.io/gh/HEPData/hepdata_lib?branch=main)
[![Documentation Status](https://readthedocs.org/projects/hepdata-lib/badge/)](http://hepdata-lib.readthedocs.io/)
[![Docker image](https://github.com/HEPData/hepdata_lib/actions/workflows/docker.yml/badge.svg)](https://github.com/HEPData/hepdata_lib/pkgs/container/hepdata_lib)

Library for getting your data into HEPData

- Documentation: https://hepdata-lib.readthedocs.io

This code works with Python 3.6, 3.7, 3.8, 3.9, 3.10, 3.11 or 3.12.

## Installation

It is highly recommended you install `hepdata_lib` into a [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/).

```shell
pip install hepdata_lib
```

If you are not sure about your Python environment, please also see below how to use `hepdata_lib` in a Docker or Apptainer container.

## Getting started

For using `hepdata_lib`, you don't even need to install it, but can use the [binder](https://mybinder.org/) or [SWAN](https://swan.cern.ch/) (CERN-only) services using one of the buttons below:

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/HEPData/hepdata_lib/main?filepath=examples/Getting_started.ipynb)
[![SWAN](https://swanserver.web.cern.ch/swanserver/images/badge_swan_white_150.png)](https://cern.ch/swanserver/cgi-bin/go/?projurl=https://github.com/HEPData/hepdata_lib.git)

You can also use the Docker image:

```shell
docker run --rm -it -p 8888:8888 -v ${PWD}:/home/hepdata ghcr.io/hepdata/hepdata_lib:latest
```

And then point your browser to [http://localhost:8888](http://localhost:8888) and use the token that is printed out. The output will end up in your current working directory (`${PWD}`).

If you prefer a shell, instead run:

```shell
docker run --rm -it -p 8888:8888 -v ${PWD}:/home/hepdata ghcr.io/hepdata/hepdata_lib:latest bash
```

If on CERN LXPLUS or anywhere else where there is Apptainer available but not Docker, you can still use the docker image:

```shell
export APPTAINER_CACHEDIR="/tmp/$(whoami)/apptainer"
apptainer shell -B /afs -B /eos docker://ghcr.io/hepdata/hepdata_lib:latest bash
```

Unpacking the image can take a few minutes the first time you use it. Please be patient. Both EOS and AFS should be available and the output will be in your current working directory.

## Further examples

There are a few more examples available that can directly be run using the [binder](https://mybinder.org/) links below or using [SWAN](https://swan.cern.ch/) (CERN-only, please use LCG release LCG_94 or later) and selecting the corresponding notebook manually:

- [Reading in text files](https://github.com/HEPData/hepdata_lib/blob/main/examples/Getting_started.ipynb)
[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/HEPData/hepdata_lib/main?filepath=examples/Getting_started.ipynb)
<br/><br/>
- [Reading in a CMS combine ntuple](https://github.com/HEPData/hepdata_lib/blob/main/examples/combine_limits.ipynb)
[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/HEPData/hepdata_lib/main?filepath=examples/combine_limits.ipynb)
<br/><br/>
- [Reading in ROOT histograms](https://github.com/HEPData/hepdata_lib/blob/main/examples/reading_histograms.ipynb)
[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/HEPData/hepdata_lib/main?filepath=examples/reading_histograms.ipynb)
<br/><br/>
- [Reading a correlation matrix](https://github.com/HEPData/hepdata_lib/blob/main/examples/correlation.ipynb)
[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/HEPData/hepdata_lib/main?filepath=examples/correlation.ipynb)
<br/><br/>
- [Reading TGraph and TGraphError from '.C' files](https://github.com/HEPData/hepdata_lib/blob/main/examples/read_c_file.ipynb)
[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/HEPData/hepdata_lib/main?filepath=examples/read_c_file.ipynb)
<br/><br/>
- [Preparing scikit-hep histograms](https://github.com/HEPData/hepdata_lib/blob/main/examples/reading_scikithep_histogram.ipynb)
[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/HEPData/hepdata_lib/main?filepath=examples/reading_scikihep_histogram.ipynb)
<br/><br/>

## External dependencies

- [ROOT](https://root.cern.ch)
- [ImageMagick](https://www.imagemagick.org)

Make sure that you have `ROOT` in your `$PYTHONPATH` and that the `convert` command is available by adding its location to your `$PATH` if needed.
