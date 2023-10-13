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

The files in which the versions are updated as well as the current version can be found in the `.bumpversion.cfg`_. You need appropriate rights for the repository to be able to push the tag.

.. _sec-dev-pypi:

Uploading to PyPI
-----------------

Once a new version has been tagged, the package should be uploaded to the Python Package Index (PyPI_).
For the markdown formatting to work, ``twine>=1.11.0`` is required.
Execute the following commands to create a source distribution and upload it:

::

    pip install -U wheel
    python setup.py sdist bdist_wheel
    pip install -U twine
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*

This uploads to the `PyPI test server`_. Mind that you need to have an account for both the test and the production servers.

Install the package for testing:

::

    pip install --index-url https://test.pypi.org/simple/ hepdata_lib

If everything is fine, upload to the production server:

::

    twine upload dist/*

You should then find the new version at `this location`_. You need to be a maintainer of the project for this to work. For more details please see the `python packaging documentation`_.


.. _bumpversion: https://github.com/peritus/bumpversion
.. _.bumpversion.cfg: https://github.com/HEPData/hepdata_lib/blob/master/.bumpversion.cfg
.. _PyPI: https://pypi.org
.. _PyPI test server: https://test.pypi.org/project/hepdata_lib/
.. _this location: https://pypi.org/project/hepdata_lib/
.. _python packaging documentation: https://packaging.python.org/tutorials/packaging-projects/

Creating a new release automatically via an issue
-------------------------------------------------

Opening an new issue automatically creates a new release if:

- The title of the issue starts with the word "release" (not case-sensitive).
- The body of the issue contains only one of the following words: "patch", "minor" or "major".

Remember to set the following github secrets: "test_pypi_password" , "pypi_password" and your personal access token to "access_token". This also uses the API token feature of PyPI.
