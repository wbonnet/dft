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

# Define the working dir, used as a target to debootstrap
rootfs_mountpoint=$(mktemp -d /tmp/lffs-test.XXXXXXXXXX)

# Default values to use when calling debootsrap
debootstrap_target="minbase"
target_version="stretch"
archive_url="http://ftp.fr.debian.org/debian"

# Create the local installation
echo "Bootstrapping a ${target_version} installation into ${rootfs_mountpoint}"
sudo debootstrap --no-check-gpg --variant="${debootstrap_target}" "${target_version}" "${rootfs_mountpoint}" "${archive_url}" > ./create-squashfs.log
echo "Bootstrapping is now finished"

# Create the squashfs file
squashfs_filename="lffs-test.squashfs"

echo "Creating squashfs ..."
sudo mksquashfs	"${rootfs_mountpoint}/" "${squashfs_filename}" -b 256K >> ./create-squashfs.log
sudo chown ${USER}:${USER} "${squashfs_filename}"
echo "Squashfs is now done"