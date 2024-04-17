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
        'kernel_name': f'python{sys.version_info.major}',
        'cwd' : 'examples'
    }

@pytest.mark.needs_root
def test_correlation(common_kwargs):# pylint: disable=redefined-outer-name
    """Tests examples/correlation.ipynb"""
    pm.execute_notebook('examples/correlation.ipynb', **common_kwargs)

def test_getting_started(common_kwargs):# pylint: disable=redefined-outer-name
    """Tests examples/Getting_started.ipynb"""
    pm.execute_notebook('examples/Getting_started.ipynb', **common_kwargs)

@pytest.mark.needs_root
def test_reading_histograms(common_kwargs):# pylint: disable=redefined-outer-name
    """Tests examples/reading_histograms.ipynb"""
    pm.execute_notebook('examples/reading_histograms.ipynb', **common_kwargs)

@pytest.mark.needs_root
def test_combine_limits(common_kwargs):# pylint: disable=redefined-outer-name
    """Tests examples/combine_limits.ipynb"""
    pm.execute_notebook('examples/combine_limits.ipynb', **common_kwargs)

@pytest.mark.needs_root
def test_c_file(common_kwargs):# pylint: disable=redefined-outer-name
    """Tests examples/read_c_file.ipynb"""
    pm.execute_notebook('examples/read_c_file.ipynb', **common_kwargs)

def test_scikithep_histograms(common_kwargs):# pylint: disable=redefined-outer-name
    """Tests examples/reading_scikithep_histograms.ipynb"""
    pm.execute_notebook('examples/reading_scikithep_histograms.ipynb', **common_kwargs)
