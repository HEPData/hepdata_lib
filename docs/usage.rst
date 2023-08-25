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

.. _here: https://github.com/HEPData/hepdata_lib/blob/master/examples/Getting_started.ipynb
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

.. _example notebook: https://github.com/HEPData/hepdata_lib/blob/master/examples/reading_histograms.ipynb

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

The Submission object is the central object where all threads come together. It represents the whole HEPData entry and thus carries the top-level meta data that is equally valid for all the tables and variables you may want to enter. The object is also used to create the physical submission files you will upload to the HEPData web interface.

When using hepdata_lib to make an entry, you **always need to create a Submission object**.
The most bare-bone submission consists of only a Submission object with no data in it:

::

    from hepdata_lib import Submission
    sub = Submission()
    outdir="./output"
    sub.create_files(outdir)

The ``create_files`` function writes all the YAML output files you need and packs them up in a ``tar.gz`` file ready to be uploaded. 

**Please note**: creating the output files also creates a ``submission`` folder containing the individual files going into the tarball. This folder exists merely for convenience, in order to make it easy to inspect each individual file. It is not recommended to attempt to manually manage or edit the files in the folder, and there is no guarantee that ``hepdata_lib`` will handle any of the changes you make in a graceful manner. As far as we are aware, there is no use case where manual editing of the files is necessary. If you have such a use case, please report it in a Github issue.

Adding links to related records
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To add a link to a related record object, you can use the `add_related_recid` function of the Submission object.

**Please note**: Values must be entered as integers.

::

    sub.add_related_recid(1)
    sub.add_related_recid(2)
    sub.add_related_recid(3)

In this example, we are adding a link to the submission with the record ID value of `"1"`.

The documentation for this feature can be found here: (`Linking Records`_).

.. _`Linking Records` : https://hepdata-submission.readthedocs.io/en/latest/bidirectional.html#linking-records


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

Binned Variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The above example uses unbinned Variables, which means that every point is simply a single number reflecting a localized value. In many cases, it is useful to use binned Variables, e.g. to represent the x axis of a histogram.
In this case, everything works the same way as in the unbinned case, except that we have to specify ``is_binned=True`` in the Variable constructor, and change how we format the list of values:

::

    mass_binned = Variable("Same mass as before, but this time it's binned",
                           is_binned=True,
                           is_independent=True)
    mass_binned.values = [ (0.5, 1.5), (1.5, 2.5), (2.5, 3.5) ]

The list of values has an entry for each bin of the Variable. The entry is a tuple, where the first entry represents the lower edge of the bin, while the second entry represents the upper edge of the bin. You can simply plug this definition into the code snippet of the unbinned case above to go from an unbinned mass to a binned value. Note that binning a Variable only really makes sense for independent variables.

Two-dimensional plots
^^^^^^^^^^^^^^^^^^^^^^^

In some cases, you may want to define information based on multiple parameters, e.g. in the case of a two-dimensional histogram (TH2 in ROOT). This can be easily accomplished by defining two independent Variables in the same Table:

::

    table = Table()

    x = Variable("Variable on the x axis",
                 is_independent=True,
                 is_binned=True)
    # x.values = [ ... ]

    y = Variable("Variable on the y axis",
                 is_independent=True,
                 is_binned=True)
    # y.values = [ ... ]

    v1 = Variable("A variable depending on x and y",
                  is_independent=False,
                  is_binned=False)
    # v1.values = [ ... ]

    v2 = Variable("Another variable depending on x and y",
                  is_independent=False,
                  is_binned=False)
    # v2.values = [ ... ]

    table.add_variable(x)
    table.add_variable(y)
    table.add_variable(v1)
    table.add_variable(v2)

Note that you can add as many dependent Variables as you would like, and that you can also make the independent variables unbinned.

One common use case with more than one independent Variable is that of correlation matrices. A detailed example implementation of this case is `available here`_.

.. _available here: https://github.com/HEPData/hepdata_lib/blob/master/examples/correlation.ipynb

Adding a  plot thumb nail to a table
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
HepData supports the addition of thumb nail images to each table. This makes it easier for the consumer of your entry to find what they are looking for, since they can simply look for the table that has the thumb nail of the plot they are interested in.
If you have the full-size plot available on your drive, you can add it to your entry very easily:

::

    table.add_image("path/to/image.pdf")

The library code then takes care of all the necessary steps, like converting the image to the right format and size, and copying it into your submission folder. The conversion relies on the ImageMagick library, and will only work if the ``convert`` command is available on your machine.

Adding keywords to a table
^^^^^^^^^^^^^^^^^^^^^^^^^^^

To make hepdata entries more searchable, keywords should be used to define what information is shown in a table. HEPData keeps track of keywords separately from the rest of the information in an entry, and provides dedicated functionalities to search for and filter by a given set of keywords. If a user is e.g. interested in finding all tables relevant to graviton production, they can do so quite easily if the tables are labelled properly. This procedure becomes much harder, or even impossible, if no keywords are used. It is therefore considered good practice to add a number of sensible keywords to your tables.

The keywords are stored as a simply dictionary for each table:

::

    table.keywords["observables"] = ["ACC", "EFF"]
    table.keywords["reactions"] = ["P P --> GRAVITON --> W+ W-", "P P --> WPRIME --> W+/W- Z0"]

In this example, we specify that the observables shown in a table are acceptance ("ACC") and efficiency ("EFF"). We also specify the reaction we are talking about, in this case graviton or W' production with decays to SM gauge bosons. This code snippet is taken from one of our `examples`_.

Lists of recognized keywords are available from the hepdata documentation for `Observables`_, `Phrases`_, and `Particles`_.

.. _`examples`: https://github.com/HEPData/hepdata_lib/blob/master/examples/Getting_started.ipynb
.. _`Observables`: https://hepdata-submission.readthedocs.io/en/latest/keywords/observables.html
.. _`Phrases`: https://hepdata-submission.readthedocs.io/en/latest/keywords/phrases.html
.. _`Particles`: https://hepdata-submission.readthedocs.io/en/latest/keywords/partlist.html


Adding links to related tables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To add a link to a related table object, you can use the `add_related_doi` function of the Table class.

**Please note**: Your DOIs must match the format: `10.17182/hepdata.[RecordID].v[Version]/t[Table]`

::

    table.add_related_doi("10.17182/hepdata.72886.v2/t3")
    table.add_related_doi("10.17182/hepdata.12882.v1/t2")

In this example, we are adding a link to the table with a DOI value of: `10.17182/hepdata.12882.v1/t2 <https://doi.org/10.17182/hepdata.12882.v1/t2>`__.


The documentation for this feature can be found here: `Linking Tables`_.

.. _`Linking Tables` : https://hepdata-submission.readthedocs.io/en/latest/bidirectional.html#linking-tables

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


