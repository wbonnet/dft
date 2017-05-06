#!/usr/bin/env bash

#
# This script is used by continous integration tools to build nightly version of the
# netshell example
#

# Stores the current working dir
WORKING_DIR=$(pwd)

# Setup virtual_env environnement
export WORKON_HOME=${WORKING_DIR}/python_virtualenvs
export VIRTUALENVWRAPPER_LOG_DIR=${WORKON_HOME}
export VIRTUALENVWRAPPER_HOOK_DIR=${WORKON_HOME}
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
source /usr/share/virtualenvwrapper/virtualenvwrapper.sh

# Create the python virtualenv
pip3 install virtualenvwrapper
mkvirtualenv dft
workon dft
pip3 install pyyaml

# Move to dft tool source dir
cd toolkit/dft

# Run the dft tool to build the root_fs
python3.5 dft build_rootfs  --project-file ${WORKING_DIR}/examples/starter-projects/netshell/project.yml --log-level debug
