#!/usr/bin/env bash

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