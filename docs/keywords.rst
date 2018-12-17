HEPData keywords
===================

To make hepdata entries more searchable, keywords can be used to define what information is shown in a table. 
The keywords are stored as a simply dictionary for each table:

::

    table.keywords["observables"] = ["ACC", "EFF"]
    table.keywords["reactions"] = ["P P --> GRAVITON --> W+ W-", "P P --> WPRIME --> W+/W- Z0"]

In this example, we specify that the observables shown in a table are acceptance ("ACC") and efficiency ("EFF"). We also specify the reaction we are talking about, in this case graviton or W' production with decays to SM gauge bosons. This code snippet is taken from one of our `examples`_.

Lists of recognized keywords are available from the hepdata documentation for `Observables`_, `Phrases`_, and `Particles`_.

.. _`examples`: https://github.com/clelange/hepdata_lib/blob/master/examples/Getting_started.ipynb
.. _`Observables`: https://hepdata-submission.readthedocs.io/en/latest/keywords/observables.html
.. _`Phrases`: https://hepdata-submission.readthedocs.io/en/latest/keywords/phrases.html
.. _`Particles`: https://hepdata-submission.readthedocs.io/en/latest/keywords/partlist.html
