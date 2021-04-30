#!/usr/bin/env bash 

# vim: ft=make ts=4 sw=4 noet
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
# Copyright 2021 DFT project (http://www.firmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#

# Activate "fail fast". Stop on first error encountered.
set -ex

# The following procedure is provided with u-boot sources in readme from doc/board folder
# The one and only argument is the target platform of u-boot build
cd  $1

# Build the required TF-A for ARM64 Rockchip SoCs platforms
[ -d arm-trusted-firmware ] && rm -fr arm-trusted-firmware
git clone https://github.com/ARM-software/arm-trusted-firmware.git
cd arm-trusted-firmware
make realclean
echo make PLAT=rk3328

# Does only copy the u-boot binary to ouput target, copying u-boot parts to the right sectors
# is done in board image definition (because an image could use somthing else than u-boot)
cp $UBOOTDIR/fip/u-boot.bin.sd.bin $1/$OUTPUT
