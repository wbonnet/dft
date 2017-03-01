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

# Defines the working directories
workdir="/home/william/Devel/dft/prototypes/squashfs-stacking/aufs-test"
configdir="${workdir}/config"
systemdir="${workdir}/system"
secretdir="${workdir}/secret"
varlogdir="${workdir}/varlog"
datadir="${workdir}/data"
volatiledir="${workdir}/volatile"
mountdir="${workdir}/mount"

# Unstack the layers

# Mount the squashfs files to a loop device
sudo umount "${mountdir}/mnt/"
sudo umount "${mountdir}/var/log"
sudo umount "${mountdir}"
sudo umount "${configdir}" 
sudo umount "${systemdir}" 
sudo umount "${secretdir}" 
sudo umount "${volatiledir}" 

