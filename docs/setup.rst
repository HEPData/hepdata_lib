Setup
=======

.. _sec-setup-users:

Setup for users
-----------------

With Python 3 locally available
+++++++++++++++++++++++++++++++

The library is available for installation as a PyPI package and can be installed from the terminal with ``pip``:


::

    pip install hepdata_lib (--user)

The ``--user`` flag lets you install the package in a user dependent location, and thus avoids writing to the location of your system's main python installation. This is useful because in many cases you, the user, do not have writing permissions to wherever the system keeps its python.

If you are running on your own computer or laptop, it's up to you to decide where you want to install the package. However, we recommended to install it inside a virtual environment (see :ref:`sec-setup-virtualenv`)

This setup naturally restricts you to use the latest stable version of the package in pypi. If you would like to use the code as it is the github repository, please follow the instructions in :ref:`sec-setup-developers`.

Using Apptainer
+++++++++++++++++++++++++++++++

On LXPLUS and many other local computing sites with CVMFS and Apptainer (previously called Singularity) available, you can use the library without having to install anything:

::

    apptainer run /cvmfs/unpacked.cern.ch/ghcr.io/hepdata/hepdata_lib:latest /bin/bash

This opens a new shell with ``hepdata_lib``, ROOT, and Python 3 available.
Your home directory and most other user directories on the machine on which you execute Apptainer will also be accessible from within this shell.
Additional directories can be made available by using the ``-B`` flag, e.g. ``-B /eos``.

If CVMFS is not available, use the following commands:

::

    export APPTAINER_CACHEDIR="/tmp/$(whoami)/apptainer"
    apptainer run docker://ghcr.io/hepdata/hepdata_lib:latest /bin/bash

Using SWAN
++++++++++

`SWAN`_ requires a CERN account. ``hepdata_lib`` should already be installed in most recent `LCG Releases`_ used by
SWAN. The latest LCG Release might not contain the latest ``hepdata_lib`` version. The `LCG Nightly`_, possibly
containing a more recent ``hepdata_lib`` version, can be used by selecting the "Bleeding Edge" software stack in the
SWAN configuration. Alternatively, you can upgrade ``hepdata_lib`` by adding a local installation path to the
``$PYTHONPATH`` in a startup script specified as the "Environment script" in the SWAN configuration (see
`Install packages in CERNBox`_). Then execute ``!pip install hepdata_lib --user --upgrade`` in your Jupyter notebook
to upgrade ``hepdata_lib`` to the latest version.

.. _SWAN: http://swan.cern.ch/
.. _LCG Releases: https://lcginfo.cern.ch/pkg/hepdata_lib/
.. _LCG Nightly: https://lcginfo.cern.ch/#nightlies
.. _Install packages in CERNBox: https://swan.docs.cern.ch/advanced/install_packages/

.. _sec-setup-developers:

Setup for developers
---------------------

The general comments about installing a python package (see :ref:`sec-setup-users`) apply here, too. Use a virtual environment (see :ref:`sec-setup-virtualenv`)!

If you would like to develop the code, you need to install the package from the up-to-date `GitHub repository`_ rather than the stable release in PyPI. To do this, you can use the pip ``-e`` syntax.
The GitHub repository can be cloned using either an `HTTPS URL`_ (``git clone https://github.com/HEPData/hepdata_lib.git``)
or an `SSH URL`_:

::

    cd $SOMEPATH
    git clone git@github.com:HEPData/hepdata_lib.git
    cd $SOMEPATH/hepdata_lib

    python3 -m venv myhepdata
    source myhepdata/bin/activate  # activate virtual environment!
    pip install -e $SOMEPATH/hepdata_lib

.. _GitHub repository: https://github.com/HEPData/hepdata_lib
.. _HTTPS URL: https://docs.github.com/en/get-started/getting-started-with-git/about-remote-repositories#cloning-with-https-urls
.. _SSH URL: https://docs.github.com/en/get-started/getting-started-with-git/about-remote-repositories#cloning-with-ssh-urls

Any changes you now make in your local copy of the repository (editing files, checking out different branches...) will be picked up by the python installation in your virtual environment.


.. _sec-setup-virtualenv:

Setting up a virtual environment
--------------------------------

The goal of a virtual environment is to have a clean python copy to work with for each of possibly many projects you work on. This makes it easy to keep track of which python packages you installed for what purpose and gives you a way of installing different versions of the package.

For documentation on how to set up and work with virtual environments, please check out `Installing packages using pip and virtual environments`_.
The venv_ module has been provided in the standard Python library since Python 3.3, avoiding the need to install
separate virtualenv_ and virtualenvwrapper_ packages as was the case with earlier Python versions.

You can create a virtual environment to work in:

::

   python3 -m venv hepdata_pypi
   source hepdata_pypi/bin/activate
   pip install hepdata_lib

You can then have a second virtual environment for installing the development branch:

::

    python3 -m venv hepdata_git
    source hepdata_git/bin/activate
    pip install -e $SOMEPATH/hepdata_lib

You can always activate the virtual environment in another shell by sourcing the relevant ``activate`` script,
which also allows you to easily switch between the two instances:

::

    source hepdata_pypi/bin/activate
    python myscript.py  # Execute script using pypi package


.. _`Installing packages using pip and virtual environments`: https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/
.. _venv: https://docs.python.org/3/library/venv.html
.. _virtualenv: https://pypi.org/project/virtualenv/
.. _virtualenvwrapper: https://virtualenvwrapper.readthedocs.io/en/latest/


Setup on lxplus with CMSSW
--------------------------

The ``hepdata_lib`` library is shipped with CMSSW via cmsdist_.
However, please make sure that you are using a recent CMSSW release, since
otherwise you might be using an outdated version of the library.
After running ``cmsenv``, you can check the installed version as follows:

::

    python3 -m pip list | grep hepdata-lib

(mind the use of ``hepdata-lib`` above, when importing, the package is still
called ``hepdata_lib``). If the version is significantly older than the one
on PyPI_, please use the Apptainer container as described at
:ref:`sec-setup-users` above.

.. _cmsdist: https://github.com/cms-sw/cmsdist/
.. _PyPI: https://pypi.org/project/hepdata-lib/
