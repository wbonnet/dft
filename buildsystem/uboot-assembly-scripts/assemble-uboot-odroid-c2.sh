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

# The first and only argument is the directory where u-boot is being built
cd  $1

# The following procedure is provided with u-boot sources in readme from doc/board folder
DIR=odroid-c2
OUTPUT=u-boot-$DIR
git clone --depth 1 https://github.com/hardkernel/u-boot.git -b odroidc2-v2015.01 $DIR
qemu-x86_64-static $DIR/fip/fip_create --bl30  $DIR/fip/gxb/bl30.bin --bl301 $DIR/fip/gxb/bl301.bin --bl31  $DIR/fip/gxb/bl31.bin --bl33  u-boot.bin $DIR/fip.bin
qemu-x86_64-static $DIR/fip/fip_create --dump $DIR/fip.bin
cat $DIR/fip/gxb/bl2.package $DIR/fip.bin > $DIR/boot_new.bin
qemu-x86_64-static $DIR/fip/gxb/aml_encrypt_gxb --bootsig --input $DIR/boot_new.bin --output $DIR/u-boot.img
dd if=$DIR/u-boot.img of=$DIR/u-boot.gxbb bs=512 skip=96
BL1=$DIR/sd_fuse/bl1.bin.hardkernel
dd if=$BL1 of=$OUTPUT conv=fsync bs=1 count=442
dd if=$BL1 of=$OUTPUT conv=fsync bs=512 skip=1 seek=1
dd if=$DIR/u-boot.gxbb of=$OUTPUT conv=fsync bs=512 seek=97
