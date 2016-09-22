#!/usr/bin/env bash

#
# The contents of this file are subject to the Apache 2.0 license you may not
# use this file except in compliance with the License.
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
#
# Copyright 2014 LFFS project (http://www.linuxfirmwarefromscratch.org).  
# All rights reserved. Use is subject to license terms.
#
#
# Contributors list :
#
#    William Bonnet   wllmbnnt@gmail.com
#
#

# Fails on error
set -e

# Defines the working directories
workdir="./unionfs-test"
lowerdir="${workdir}/lowerdir"
upperdir="${workdir}/upperdir"
mergedir="${workdir}/mergedir"

# Make sure the directories exist
mkdir -p "${workdir}"
mkdir -p "${lowerdir}"
mkdir -p "${upperdir}"
mkdir -p "${mergedir}"

# Mount and stack the layers
sudo mount -t squashfs lffs-test.squashfs "${lowerdir}" -o loop
sudo mount -t unionfs -o dirs=${upperdir}=rw:${lowerdir}=ro unionfs ${mergedir}
