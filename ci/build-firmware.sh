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
python3.5 dft build_rootfs  --project-file ${WORKING_DIR}/${DFT_PROJECT} --log-level debug --keep-bootstrap-files

# Run the dft tool to build the firmware
python3.5 dft install_bootchain --project-file ${WORKING_DIR}/${DFT_PROJECT} --log-level debug

# Run the dft tool to build the firmware
python3.5 dft build_firmware --project-file ${WORKING_DIR}/${DFT_PROJECT} --log-level debug

# Run the dft tool to assemble the firmware scripts
python3.5 dft assemble_firmware --project-file ${WORKING_DIR}/${DFT_PROJECT} --log-level debug

# Create the image from the generated rootfs
sudo python3.5 dft build_image --project-file ${WORKING_DIR}/${DFT_PROJECT} --log-level debug

# Go back to startup directory and clean working directory
cd ${WORKING_DIR}
sudo rm -fr ${WORKING_DIR}/working_dir/*/rootfs
