Contributing
=======================

Here are a couple of details regarding the development of this library. Contributions are more than welcome!

Please see :ref:`sec-setup-developers` on how to set up the library for development.

- :ref:`sec-dev-bumpversion` to tag a new release
- :ref:`sec-dev-pypi`

.. _sec-dev-bumpversion:

Using bumpversion
-----------------------------

bumpversion_ allows to update the library version consistently over all files. Please do not change the version manually, but use the following steps instead after a pull request has been merged into the ``main`` branch. Depending on the amount of changes, choose accordingly from:

- ``patch`` = ``+0.0.1``
- ``minor`` = ``+0.1.0``
- ``major`` = ``+1.0.0``

Execute the following commands:

::

    pip install --upgrade bumpversion
    git checkout main
    git pull
    bumpversion patch # adjust accordingly
    git push origin main --tags

The files in which the versions are updated as well as the current version can be found in the `.bumpversion.cfg`_. You need appropriate rights for the repository to be able to push the tag.

.. _sec-dev-pypi:

Creating a new release
---------------------------

Once a new version has been tagged, a new release has to be created on GitHub.
Go to `Releases`_ and click on "Draft a new release".
Choose the tag you just created, auto-generate release notes, and click "Publish release".
The package will then be automatically uploaded to the Python Package Index (PyPI_) at `this location`_
and a new container image will be built and tagged.

.. _bumpversion: https://github.com/peritus/bumpversion
.. _.bumpversion.cfg: https://github.com/HEPData/hepdata_lib/blob/main/.bumpversion.cfg
.. _Releases: https://github.com/HEPData/hepdata_lib/releases
.. _PyPI: https://pypi.org
.. _PyPI test server: https://test.pypi.org/project/hepdata_lib/
.. _this location: https://pypi.org/project/hepdata_lib/
