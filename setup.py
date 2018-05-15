"""pypi package setup."""
from __future__ import print_function
import codecs
import os
from os import path
import subprocess
import sys
#~ from ctypes import cdll
from setuptools import setup, find_packages

def root_install():
    """Make sure ROOT is installed before import"""
    try:
        import ROOT #pylint: disable=unused-variable
        print("setup.py: ROOT already installed.")
    except ImportError:
        print("setup.py: Installing ROOT.")
        url = "https://root.cern.ch/download/root_v6.12.06.Linux-ubuntu14-x86_64-gcc4.8.tar.gz"
        subprocess.call(["curl", "-O", url])
        subprocess.call(["tar", "xzf", path.basename(url)])

        cmd = ["bash", "-c", "cd root && source bin/thisroot.sh && env"]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        #~ for lib in [x for x in os.listdir("./root/lib") if x.endswith(".so")]:
            #~ try:
                #~ cdll.LoadLibrary('./root/lib/'+lib)
            #~ except:
                #~ continue
        try:
            os.execv(sys.argv[0], sys.argv)
        except OSError, exc:
            print('Failed re-exec:', exc)
            sys.exit(1)

        for line in proc.stdout:
            (key, _, value) = line.partition("=")
            value = value.strip("\n")
            os.environ[key] = value
            if(key in ["PYTHONPATH", "LIBPATH", "BIN_PATH", "ROOTSYS", "LD_LIBRARY_PATH"]):
                for part in value.split(":"):
                    sys.path.append(part)
            print(key, value)
        print(sys.path)
        proc.communicate()
        import ROOT #pylint: disable=unused-variable

root_install()

DEPS = ['numpy', 'PyYAML']

HERE = path.abspath(path.dirname(__file__))

with codecs.open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='hepdata_lib',
    version='0.1.1',
    description='Library for getting your data into HEPData',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/clelange/hepdata_lib',
    author='Andreas Albert, Clemens Lange',
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
    install_requires=DEPS,
    setup_requires=['pytest-runner', 'pytest-pylint'],
    tests_require=['pytest', 'pylint'],
    project_urls={
        'Documentation': 'https://hepdata-lib.readthedocs.io',
        'Bug Reports': 'https://github.com/clelange/hepdata_lib/issues',
        'Source': 'https://github.com/clelange/hepdata_lib',
    }, )
