from setuptools import setup, find_packages
from codecs import open
from os import path

deps = [
      'numpy',
      'PyYAML'
]

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='hepdata_lib',
      version='0.1',
      description='Library for getting your data into HEPData',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://github.com/clelange/hepdata_lib',
      author='Clemens Lange',
      author_email='clemens.lange@cern.ch',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
      ],
      keywords='HEPData physics OpenData',
      packages=find_packages(exclude=['contrib', 'docs', 'tests']),
      zip_safe=False,
      install_requires=deps,
      project_urls={
        'Bug Reports': 'http://github.com/clelange/hepdata_lib/issues',
        'Source': 'http://github.com/clelange/hepdata_lib',
      },
      test_suite='nose.collector',
      tests_require=['nose']
      )
