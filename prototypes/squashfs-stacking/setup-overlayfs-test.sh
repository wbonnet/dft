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
# Copyright 2016 DFT project (http://www.debianfirmwaretoolkit.org).  
# All rights reserved. Use is subject to license terms.
#
# Debian Firmware Toolkit is the new name of Linux Firmware From Scratch
# Copyright 2014 LFFS project (http://www.linuxfirmwarefromscratch.org).  
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#

# Fails on error
set -e

# Defines the working directories
testdir="./overlayfs-test"
configdir="${testdir}/config"
systemdir="${testdir}/system"
secretdir="${testdir}/secret"
varlogdir="${testdir}/varlog"
datadir="${testdir}/data"
volatiledir="${testdir}/volatile"
mountdir="${testdir}/mount"
workdir="${testdir}/workdir"


# Make sure the directories exist
mkdir -p "${testdir}"

sudo mount -t tmpfs -o size=1G,nr_inodes=10k,mode=700 tmpfs "${testdir}"

sudo mkdir -p "${configdir}"
sudo mkdir -p "${systemdir}"
sudo mkdir -p "${secretdir}"
sudo mkdir -p "${varlogdir}"
sudo mkdir -p "${volatiledir}"
sudo mkdir -p "${datadir}"
sudo mkdir -p "${workdir}"

# Make sure the volatile directories exist
sudo mkdir -p "${mountdir}"

# Mount the squashfs files to a loop device
sudo mount -t squashfs config.fw "${configdir}" -o loop
sudo mount -t squashfs system.fw "${mountdir}" -o loop
sudo mount -t squashfs secret.fw "${secretdir}" -o loop

# Stacks the layers
sudo mount -t overlay overlay -olowerdir=${configdir}:${mountdir}/etc ${mountdir}/etc
sudo mount -t overlay overlay -olowerdir=${secretdir}:${mountdir}/etc/ ${mountdir}/etc/
sudo mount -t overlay overlay -olowerdir=${mountdir}/var/log,upperdir=${varlogdir},workdir=${workdir} ${mountdir}/var/log/
sudo mount -t overlay overlay -olowerdir=${mountdir}/mnt,upperdir=${datadir},workdir=${workdir} ${mountdir}/mnt/
# sudo mount -t overlay overlay -olowerdir=${mountdir},upperdir=${volatiledir},workdir=${workdir} ${mountdir}


# mkdir -p /tmp/olay /tmp/sfs
# mount -t tmpfs none /tmp/olay
# mkdir /tmp/olay/up /tmp/olay/wrk
# mount ./my.sfs /tmp/sfs
# mount -t overlay overlay -olowerdir=/tmp/sfs,upperdir=/tmp/olay/up,workdir=/tmp/olay/‌​workdir /tmp/olay

