Contributing
=======================

Here are a couple of details regarding the development of this library. Contributions are more than welcome!

Please see :ref:`sec-setup-developers` on how to set up the library for development.

- :ref:`sec-dev-bumpversion` to tag a new release
- :ref:`sec-dev-pypi`

.. _sec-dev-bumpversion:

Using bumpversion
-----------------------------

bumpversion_ allows to update the library version consistently over all files. Please do not change the version manually, but use the following steps instead after a pull request has been merged into the ``master`` branch. Depending on the amount of changes, choose accordingly from:

- ``patch`` = ``+0.0.1``
- ``minor`` = ``+0.1.0``
- ``major`` = ``+1.0.0``

Execute the following commands:

::

    pip install --upgrade bumpversion
    git checkout master
    git pull
    bumpversion patch # adjust accordingly
    git push origin master --tags

The files in which the versions are updated as well as the current version can be found in the `.bumpversion.cfg`_

.. _sec-dev-pypi:

Uploading to PyPI
-----------------------------

Once a new version has been tagged, the package should be uploaded to the Python Package Index (PyPI).

.. _bumpversion: https://github.com/peritus/bumpversion
.. _.bumpversion.cfg: https://github.com/clelange/hepdata_lib/blob/master/.bumpversion.cfg