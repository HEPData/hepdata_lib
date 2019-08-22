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

    pip3 install --upgrade enum34 pytest_pylint configparser astroid coveralls

elif [[ "$TRAVIS_OS_NAME" == "linux" ]]; then
    curl -O https://root.cern.ch/download/root_v6.12.06.Linux-ubuntu14-x86_64-gcc4.8.tar.gz
    tar xzf root_v6.12.06.Linux-ubuntu14-x86_64-gcc4.8.tar.gz

    sudo sed -i '/MVG/d' /etc/ImageMagick-6/policy.xml
    sudo sed -i '/PDF/{s/none/read|write/g}' /etc/ImageMagick-6/policy.xml
    sudo sed -i '/PDF/ a <policy domain="coder" rights="read|write" pattern="LABEL" />' /etc/ImageMagick-6/policy.xml

    pip install --upgrade enum34 pytest_pylint configparser astroid coveralls

    sudo apt update
    sudo apt install -y ghostscript
fi
