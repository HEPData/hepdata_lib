"""Test notebooks."""
import sys
import pytest
import papermill as pm

@pytest.fixture()
def common_kwargs(tmpdir):
    """Set common_kwargs"""
    outputnb = tmpdir.join('output.ipynb')
    return {
        'output_path': str(outputnb),
        'kernel_name': 'python{}'.format(sys.version_info.major),
        'cwd' : str('examples')
    }

def test_correlation(common_kwargs):# pylint: disable=redefined-outer-name
    """Tests examples/correlation.ipynb"""
    pm.execute_notebook('examples/correlation.ipynb', **common_kwargs)

def test_getting_started(common_kwargs):# pylint: disable=redefined-outer-name
    """Tests examples/Getting_started.ipynb"""
    pm.execute_notebook('examples/Getting_started.ipynb', **common_kwargs)

def test_reading_histograms(common_kwargs):# pylint: disable=redefined-outer-name
    """Tests examples/reading_histograms.ipynb"""
    pm.execute_notebook('examples/reading_histograms.ipynb', **common_kwargs)

def test_combine_limits(common_kwargs):# pylint: disable=redefined-outer-name
    """Tests examples/combine_limits.ipynb"""
    pm.execute_notebook('examples/combine_limits.ipynb', **common_kwargs)