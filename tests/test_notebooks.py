import sys
import os
import papermill as pm
import pytest

@pytest.fixture()
def common_kwargs(tmpdir):
    outputnb = tmpdir.join('output.ipynb')
    return {
        'output_path': str(outputnb),
        'kernel_name': 'python{}'.format(sys.version_info.major),
        'cwd' : str('examples')
    }

def test_correlation(common_kwargs):
    pm.execute_notebook('examples/correlation.ipynb', **common_kwargs)

def test_Getting_started(common_kwargs):
    pm.execute_notebook('examples/Getting_started.ipynb', **common_kwargs)

def test_reading_histograms(common_kwargs):
    pm.execute_notebook('examples/reading_histograms.ipynb', **common_kwargs)

def test_combine_limits(common_kwargs):
    pm.execute_notebook('examples/combine_limits.ipynb', **common_kwargs)

