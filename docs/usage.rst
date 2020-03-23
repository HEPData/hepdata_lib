Usage
=======================

The library aims to offer tools for two main operations:

* :ref:`sec-usage-reading` from the usual formats (ROOT, text files, etc.) into python lists.
* :ref:`sec-usage-writing` from python lists to the HEPData YAML-based format

All of this happens in a user-friendly python interface. :ref:`sec-usage-reading` is helpful if you need help getting your data as a python list. If you already have your data accessible in python, great! Skip right ahead to :ref:`sec-usage-writing`.

In the following sections, there are

HEPData and its data format
-----------------------------

The HEPData data model revolves around **Tables** and **Variables**. At its core, a Variable is a one-dimensional array of numbers with some additional (meta-)data, such as uncertainties, units, etc. assigned to it. A Table is simply a set of multiple Variables. This definition will immediately make sense to you when you think of a general table, which has multiple columns representing different variables.


.. _sec-usage-reading:

Reading data
-------------------------------

Reading from plain text
+++++++++++++++++++++++++++++++

If you save your data in a text file, a simple-to-use tool is the ``numpy.loadtxt`` function,
which loads column-wise data from plain-text files and returns it as a ``numpy.array``.

::

    import numpy as np
    my_array = np.loadtxt("some_file.txt")

A detailed example is available here_.
For documentation on the `loadtxt` function, please refer the `numpy documentation`_.

.. _here: https://github.com/clelange/hepdata_lib/blob/master/examples/Getting_started.ipynb
.. _numpy documentation: https://docs.scipy.org/doc/numpy/reference/generated/numpy.loadtxt.html


Reading from ROOT files
+++++++++++++++++++++++++++++++

In many cases, data in the experiments is available as one of various ROOT data types, such as ``TGraphs``, ``TH1``, ``TH2``, etc, which are saved in ``*.root`` files.

To facilitate reading these objects, the ``RootFileReader`` class is provided.
The reader is instantiated by passing a path to the ROOT file to read from:

::

    from hepdata_lib import RootFileReader
    reader = RootFileReader("/path/to/myfile.root")

After initialization, individual methods are provided for access to different types of objects stored in the file.

* Reading TGraph, TGraphErrors, TGraphAsymmErrors: ``RootFileReader.read_graph``
* Reading TH1: ``RootFileReader.read_hist_1d``
* Reading TH2: ``RootFileReader.read_hist_2d``

While the details of each function are adapted to their respective use cases, they follow a common input/output logic. The methods are called by providing the path to the object inside the ROOT file. They return a dictionary containing lists of all relevant numbers that can be extracted from the object, such as x values, y values, uncertainties, etc.

As an example, if a TGraph is saved as with name ``mygraph`` in the directory ``topdir/subdir`` inside the ROOT file, it can be retrieved as:

::

    data = reader.read_graph("topdir/subdir/mygraph")

Since a graph is simply a set of (x,y) pairs for each point, the ``data`` dictionary will have two key/value pairs:

* key "x" -> list of x values.
* key "y" -> list of y values.

More complex information will be returned for ``TGraphErrors``, etc, which can also be read in this manner.
For detailed descriptions of the extraction logic and returned data, please refer to the documentation of the individual methods.

An `example notebook`_ shows how to read histograms from a ROOT file.

.. _example notebook: https://github.com/clelange/hepdata_lib/blob/master/examples/reading_histograms.ipynb

.. _sec-usage-writing:

Writing data
-------------------------------

Following the HEPData data model, the hepdata_lib implements four main classes for writing data:

* **Submission**
* **Table**
* **Variable**
* **Uncertainty**


.. _sec-usage-submission:

The Submission object
+++++++++++++++++++++++++++++++

The Submission object is the central object where all threads come together. The Submission object represents the whole HEPData entry and thus carries the top-level meta data that is equally valid for all the tables and variables you may want to enter. The object is also used to create the physical submission files you will upload to the HEPData web interface.

When using the hepdata_lib to make an entry, you **always need to create a Submission object**.
The most bare-bone submission consists of only a Submission object with no data in it:

::

    from hepdata_lib import Submission
    sub = Submission()
    outdir="./output"
    sub.create_files(outdir)

The ``create_files`` function writes all the YAML output files you need and packs them up in a ``tar.gz`` file ready to be uploaded.


.. _sec-usage-tab-var:

Tables and Variables
+++++++++++++++++++++++++++++++

The real data is stored in Variables and Tables. Variables come in two flavors: *independent* and *dependent*. Whether a variable is independent or dependent may change with context, but the general idea is that the independent variable is what you put in, the dependent variable is what comes out. Example: if you calculate a cross-section limit as a function of the mass of a hypothetical new particles, the mass would be independent, the limit dependent. The number of either type of variables is not limited, so if you have a scenario where you give N results as a function of M model parameters, you can have N dependent and M independent variables.
All the variables are then bundled up and added into a Table object.

Let's see what this looks like in code:

::

    from hepdata_lib import Variable

    mass = Variable("Graviton mass",
                    is_independent=True,
                    is_binned=False,
                    units="GeV")
    mass.values = [ 1, 2, 3 ]

    limit = Variable("Cross-section limit",
                    is_independent=False,
                    is_binned=False,
                    units="fb")

    limit.values = [ 10, 5, 2 ]

    table = Table("Graviton limits")
    table.add_variable(mass)
    table.add_variable(limit)

That's it! We have successfully created the Table and Variables and stored our results in them. The only task left is to tell the Submission object about our new Table:

::

    sub.add_table(table)


After we have done this, the table will be included in the output files the ``Submission.create_files`` function writes (see  :ref:`sec-usage-submission`).



Uncertainties
++++++++++++++++++++++++++++++++

In many cases, you will want to give uncertainties on the central values provided in the Variable objects. Uncertainties can be *symmetric* or *asymmetric* (up and down variations of the central value either have the same or different magnitudes). For symmetric uncertainties, the values of the uncertainties are simply stored as a one-dimensional list. For asymmetric uncertainties, the up- and downward variations are stored as a list of two-component tuples:

::

    from hepdata_lib import Uncertainty
    unc1 = Uncertainty("A symmetric uncertainty", is_symmetric=True)
    unc1.values = [ 0.1, 0.3, 0.5]

    unc2 = Uncertainty("An asymmetric uncertainty", is_symmetric=False)
    unc2.values = [ (-0.08, +0.15), (-0.13, +0.20), (-0.18,+0.27) ]

After creating the Uncertainty objects, the only additional step is to attach them to the Variable:

::

    variable.add_uncertainty(unc1)
    variable.add_uncertainty(unc2)


