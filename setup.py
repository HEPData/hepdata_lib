"""pypi package setup."""
import codecs
from os import path
from setuptools import setup, find_packages
try:
    import ROOT  # pylint: disable=W0611
except ImportError:
    print("ROOT is required by this library.")

with open("requirements.txt") as f:
    DEPS = f.readlines()

HERE = path.abspath(path.dirname(__file__))

with codecs.open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='hepdata_lib',
    version='0.20.0',
    description='Library for getting your data into HEPData',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/HEPData/hepdata_lib',
    author='Andreas Albert, Clemens Lange',
    author_email='hepdata-lib@cern.ch',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
    keywords='HEPData physics OpenData',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    zip_safe=False,
    python_requires='>=3.6',
    install_requires=DEPS,
    extras_require={
        'test': [
            'ipykernel',
            'papermill',
            'pylint',
            'pytest',
            'pytest-cov',
        ]
    },
    project_urls={
        'Documentation': 'https://hepdata-lib.readthedocs.io',
        'Bug Reports': 'https://github.com/HEPData/hepdata_lib/issues',
        'Source': 'https://github.com/HEPData/hepdata_lib',
    }, )
