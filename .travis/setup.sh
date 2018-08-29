#!/bin/bash
# fail script immediately on any errors in external commands
set -e

source ./.travis/travis_wait.sh

if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then
    brew update
    brew cask uninstall --force oclint
    brew upgrade python cmake libpng libtiff
    # Install ROOT dependencies
    brew install ossp-uuid davix isl libmpc gcc fftw freetype fontconfig webp gd graphviz gsl lz4 tbb xrootd
    echo "Installing ROOT"
    # travis_wait 45 brew install root
    curl -O https://clange.web.cern.ch/clange/root-v6.14.02.tar.gz
    tar xzf root-v6.14.02.tar.gz
    mkdir -p /usr/local/Cellar/root
    mv 6.14.02 /usr/local/Cellar/root/

    # Workaround for buggy PyYaml v 3.12 on pypi
    # Can be removed once PyYaml 3.13 is released
    pip3 install git+https://github.com/yaml/pyyaml@b6cbfeec35e019734263a8f4e6a3340e94fe0a4f
    pip3 install --upgrade enum34 pytest_pylint configparser astroid coveralls

elif [[ "$TRAVIS_OS_NAME" == "linux" ]]; then
    curl -O https://root.cern.ch/download/root_v6.12.06.Linux-ubuntu14-x86_64-gcc4.8.tar.gz
    tar xzvf root_v6.12.06.Linux-ubuntu14-x86_64-gcc4.8.tar.gz

    # Workaround for buggy PyYaml v 3.12 on pypi
    # Can be removed once PyYaml 3.13 is released
    pip install git+https://github.com/yaml/pyyaml@b6cbfeec35e019734263a8f4e6a3340e94fe0a4f
    pip install --upgrade enum34 pytest_pylint configparser astroid coveralls
fi
