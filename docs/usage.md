# Using the hepdata_lib
The library aims to offer tools for two main operations:
* **Reading data** from the usual formats (ROOT, text files, etc.)
* **Writing data** in the HEPData YAML-based format
All of this happens in a user-friendly python interface.

In the following sections, there are

## HEPData and its format

The HEPData data model revolves around **Tables** and **Variables**. At its core, a Variable is a one-dimensional array of numbers with some additional (meta-)data, such as uncertainties, units, etc. assigned to it. A Table is simply a set of multiple Variables. This definition will immediately make sense to you when you think of a general table, which has multiple columns representing different variables.



## Reading data

### Examples

## Writing data
Following the HEPData data model, the hepdata_lib implements four main classes for writing data:
* **Submission**
* **Table**
* **Variable**
* **Uncertainty**

### Step-by-step
#### The Submission object
The Submission object is the central object where all threads come together. The Submission object represents the whole HEPData entry and thus carries the top-level meta data that is equally valid for all the tables and variables you may want to enter. The object is also used to create the physical submission files you will upload to the HEPData web interface.

When using the hepdata_lib to make an entry, you **always need to create a Submission object**.
The most bare-bone submission consists of only a Submission object with no data in it:
```
from hepdata_lib import Submission
sub = Submission()
outdir="./output"
sub.create_files(outdir)
```
The `create_files` function writes all the YAML output files you need and packs them up in a `tar.gz` file ready to be uploaded.

#### Tables and Variables
The real data is stored in Variables and Tables. Variables come in two flavors: *independent* and *dependent*. Whether a variable is independent or dependent may change with context, but the general idea is that the independent variable is what you put in, the dependent variable is what comes out. If you have a typical one-dimensional plot, where you show a cross-section limit as a function of the mass of a hypothetical new particles, the mass would be independent, the limit dependent. The number of variables is not limited, e.g. if you have a scenario where you give N results as a function of M model parameters, you can also have M independent and N dependent variables. All the variables are then bundled up and added into a Table object.



Let's see what this looks like in code:

```
from hepdata_lib import Variable

mass = Variable("Graviton mass",
                is_independent=True,
                is_binned=False,
                units="GeV")

limit = Variable("Cross-section limit",
                 is_independent=False,
                 is_binned=False,
                 units="fb")

table = Table("Graviton limits")
table.add_variable(mass)
table.add_variable(limit)
```


