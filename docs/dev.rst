Developer information
=====================

The testing system
------------------

While further developing the code base, we want to ensure that any changes we make do not accidentally break existing functionality. For this purpose, we use continuous integration via GitHub Actions_. Practically, this means that we define a set of test code that is automatically run in a predefined environment every time we push to a branch or create a pull request. If the test code runs successfully, we know that everything works as expected.

To run the tests, move into the ``hepdata_lib`` directory while in your virtual environment and run

::

    pip install -e ".[test]"
    pytest tests

It is a good idea to run the tests manually to ensure that your changes do not cause any issues.

Definition of test cases
++++++++++++++++++++++++

Test cases are defined in the ``test`` subfolder of the repository. Independent sets of test code are defined in individual files in that directory, with each files being named like ``test_*.py``.

Inside each file, a test class is defined that inherits from the ``TestCase`` class from the ``unittest`` package. The actual code to be run is then implemented as functions of the test object, and all functions named ``test_*`` will be run automatically. Example:

::

    from unittest import TestCase

    class TestForFeatureX(TestCase):
        """Test case for feature X."""

        def test_aspect_y(self):
            """Test that aspect Y works."""
            # Do something with feature X and sub-feature Y."""

        def test_aspect_z(self):
            """Test that aspect Z works."""
            # Do something with feature X and sub-feature Z."""

If all functions run without raising exceptions, the test is considered to be passed. Therefore, you should ensure that the test functions only run through if everything is really as expected.


When to test
~~~~~~~~~~~~

Tests should be added any time functionality is added. If functionality is modified, so should the tests.

What to test
~~~~~~~~~~~~

Generally, the tests should ensure that the code behaves as expected, whatever that may mean. They should be sufficiently rigorous to make sure that nothing can break silently, and that outputs are correct.

Broad inspiration for aspects to check:

* Are all inputs handled gracefully? What happens if an inconsistent input type is provided?
* Is the output correct for a variety of plausible inputs?
* If the tested code can raise exceptions: Is the exceptions really raised if and only if the expected criteria are met?


How to test
~~~~~~~~~~~

The ``TestCase`` base class provides functionality to help implement simple checks to verify the behavior. A test can immediately be made to fail by calling ``self.fail()``. For convenience, additional functions like ``assertTrue``, ``assertFalse``, etc. are provided, which work like normal python assertions. If the assertion fails, the test is considered to be failed. Additionally, the ``assertRaises`` method can be used as a context to ensure that exceptions are raised as expected. Here's a simple example:

::

    class TestForArithmetic(TestCase):
        """Test case for python arithmetic"""

        def test_addition(self):
            """Test that the addition operator works."""

            # This will fail the test if 1+1 is not equal to 2
            self.assertTrue(1+1 == 2)

            # Equivalent implementation using the explicit fail method:
            if 1+1 != 2:
                self.fail()

        def test_addition_exception(self):
            """Test that the addition operator raises the right exceptions."""

            # Check that it raises an expected TypeError for bad input
            with self.assertRaises(TypeError):
                val = None + 5

            # Check that no TypeError is raised for good input
            try:
                val = 1 + 5
            except TypeError:
                self.fail("The addition operator raised an unexpected TypeError.")



Note that this is an overly simple example case: In a real testing case, you should try to cover all possible and impossible input types for a thorough test coverage.

Check out the unittest package documentation_ for details of the available testing functionality.

.. _Actions: https://docs.github.com/en/actions
.. _documentation: https://docs.python.org/2/library/unittest.html#unittest.TestCase


Building the documentation
--------------------------

After installing the ``hepdata_lib`` package, move into the ``hepdata_lib/docs`` directory and install the additional necessary packages into your virtual environment:

::

    pip install -r requirements.txt

Then you can build the documentation locally with Sphinx using ``make html`` and view the output by opening a web browser at ``_build/html/index.html``.
In addition, please also test whether building the LateX (``make latexpdf``) and epub (``make epub``) versions works.


Analysing the code
------------------

::

    pylint hepdata_lib/*.py
    pylint tests/*.py --rcfile=tests/pylintrc

These commands are run by GitHub Actions (for Python 3.8 or later),
so you should first check locally that no issues are flagged.


Making a release
----------------

After making a new release available on `PyPI`_, a `JIRA`_ issue (`example`_) should be opened to request that
``hepdata_lib`` is upgraded in future `LCG Releases`_ used by `SWAN`_.

.. _PyPI: https://pypi.org/project/hepdata-lib/
.. _JIRA: https://its.cern.ch/jira/projects/SPI/
.. _example: https://its.cern.ch/jira/browse/SPI-2507
.. _LCG Releases: https://lcginfo.cern.ch/pkg/hepdata_lib/
.. _SWAN: http://swan.cern.ch/