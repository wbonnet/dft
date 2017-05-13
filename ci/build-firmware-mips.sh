#!/usr/bin/env bash

#
# This script is used by continous integration tools to build nightly version of the
# netshell example
#

# Stop a first error
set -e

# Retrive the project filename from the command line
DFT_PROJECT=$1

# Stores the current working dir
WORKING_DIR=$(pwd)

# Setup virtual_env environnement
export WORKON_HOME=${WORKING_DIR}/python_virtualenvs
export VIRTUALENVWRAPPER_LOG_DIR=${WORKON_HOME}
export VIRTUALENVWRAPPER_HOOK_DIR=${WORKON_HOME}
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
source /usr/share/virtualenvwrapper/virtualenvwrapper.sh

# Move to dft tool source dir
cd toolkit/dft

# Run the dft tool to build the root_fs
python3.5 dft build_rootfs  --project-file ${WORKING_DIR}/${DFT_PROJECT} --log-level debug --keep-bootstrap-files --limit-arch mips

# Go back to startup directory and clean working directory
cd ${WORKING_DIR}
sudo rm -fr ${WORKING_DIR}/working_dir/*/rootfs
