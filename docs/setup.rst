Setup
=======

.. _sec-setup-users:

Setup for users
-----------------

The library is available for installation as a pypi package and can be installed with pip:


::

    pip install hepdata_lib (--user)

The ``--user`` flag lets you install the package in a user dependent location, and thus avoids writing to the location of your system's main python installation. This is useful because in many cases you, the user, do not have writing permissions to wherever the system keeps its python.

If you are running on your own computer or laptop, it's up to you to decide where you want to install the package. However, we recommended to install it inside a virtual environment (see :ref:`sec-setup-virtualenv`)

This setup naturally restricts you to use the latest stable version of the package in pypi. If you would like to use the code as it is the github repository, please follow the instructions in :ref:`sec-setup-developers`.


.. _sec-setup-developers:

Setup for developers
---------------------

The general comments about installing a python package (see :ref:`sec-setup-users`) apply here, too. Use a virtual environment (see :ref:`sec-setup-virtualenv`)!

If you would like to develop the code, you need to install the package from the up-to-date git repository rather than the stable release in pypi. To do this, you can use the pip `-e` syntax:

::
    
    cd $SOMEPATH
    git clone git@github.com:clelange/hepdata_lib.git

    workon myhepdata # activate virtual environment!
    pip install -e $SOMEPATH/hepdata_lib

Any changes you now make in your local copy of the repository (editing files, checking out different branches...) will be picked up by the python installation in your virtual environment.


.. _sec-setup-virtualenv:

Setting up a virtual environment
--------------------------------

TODO
