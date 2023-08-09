Setup
=======

.. _sec-setup-users:

Setup for users
-----------------

With Python 3 locally available
+++++++++++++++++++++++++++++++

The library is available for installation as a pypi package and can be installed from the terminal with pip:


::

    pip install hepdata_lib (--user)

The ``--user`` flag lets you install the package in a user dependent location, and thus avoids writing to the location of your system's main python installation. This is useful because in many cases you, the user, do not have writing permissions to wherever the system keeps its python.

If you are running on your own computer or laptop, it's up to you to decide where you want to install the package. However, we recommended to install it inside a virtual environment (see :ref:`sec-setup-virtualenv`)

This setup naturally restricts you to use the latest stable version of the package in pypi. If you would like to use the code as it is the github repository, please follow the instructions in :ref:`sec-setup-developers`.

Using Singularity/Apptainer
+++++++++++++++++++++++++++++++

On LXPLUS and many other local computing sites with CVMFS and Singularity/Apptainer available, you can use the library without having to install anything:

::

    apptainer run /cvmfs/unpacked.cern.ch/ghcr.io/hepdata/hepdata_lib:latest /bin/bash

This opens a new shell with ``hepdata_lib``, ROOT, and Python 3 available.
Your home directory and most other user directories on the machine on which you execute Singularity/Apptainer will also be accessible from within this shell.


.. _sec-setup-developers:

Setup for developers
---------------------

The general comments about installing a python package (see :ref:`sec-setup-users`) apply here, too. Use a virtual environment (see :ref:`sec-setup-virtualenv`)!

If you would like to develop the code, you need to install the package from the up-to-date git repository rather than the stable release in pypi. To do this, you can use the pip `-e` syntax:

::

    cd $SOMEPATH
    git clone git@github.com:HEPData/hepdata_lib.git

    workon myhepdata # activate virtual environment!
    pip install -e $SOMEPATH/hepdata_lib

Any changes you now make in your local copy of the repository (editing files, checking out different branches...) will be picked up by the python installation in your virtual environment.


.. _sec-setup-virtualenv:

Setting up a virtual environment
--------------------------------

The goal of a virtual environment is to have a clean python copy to work with for each of possibly many projects you work on. This makes it easy to keep track of which python packages you installed for what purpose and gives you a way of installing different versions of the package.

For documentation on how to set up and work with virtual environments, please check out the virtualenv_ and virtualenvwrapper_ packages.

.. _virtualenv: https://pypi.org/project/virtualenv/
.. _virtualenvwrapper: https://virtualenvwrapper.readthedocs.io/en/latest/

Once you have both of them setup, you can create a virtual environment to work in:

::

   mkvirtualenv hepdata_pypi
   pip install hepdata_lib

You can then have a second virtual environment for installing the development branch:

::

    mkvirtualenv hepdata_git
    pip install -e $SOMEPATH/hepdata_lib

You can always activate the virtual environment in another shell by calling the workon command, which also allows you to easily switch between the two instances:

::

    workon hepdata_pypi
    python myscript.py # Execute script using pypi package


    workon hepdata_git
    python myscript.py # Execute script using development branch


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
on PyPI_, please use the Singularity/Apptainer container as described at
:ref:`sec-setup-users` above.

.. _cmsdist: https://github.com/cms-sw/cmsdist/
.. _PyPI: https://pypi.org/project/hepdata-lib/
