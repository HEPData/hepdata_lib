#!/bin/bash

if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then
    brew update
    brew cask uninstall --force oclint
    brew upgrade python
    brew install root
elif [[ "$TRAVIS_OS_NAME" == "linux" ]]; then
    curl -O https://root.cern.ch/download/root_v6.12.06.Linux-ubuntu14-x86_64-gcc4.8.tar.gz
    tar xzvf root_v6.12.06.Linux-ubuntu14-x86_64-gcc4.8.tar.gz
fi

# Workaround for uggy PyYaml v 3.12 on pypi
# Can be removed once PyYaml 3.13 is released
mkdir ./yaml
easy_install --prefix="./yaml" git+https://github.com/yaml/pyyaml
