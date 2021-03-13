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
GITHUBDIR=odroid-c4
OUTPUT=u-boot-odroid-c4
UBOOTDIR=$1/$GITHUBDIR
git clone --depth 1 https://github.com/hardkernel/u-boot.git -b odroidg12-v2015.01 $UBOOTDIR

mkdir -p $UBOOTDIR/fip
chmod +x $UBOOTDIR/fip/blx_fix.sh
wget https://github.com/BayLibre/u-boot/releases/download/v2017.11-libretech-cc/blx_fix_g12a.sh -O fip/blx_fix.sh
cp $UBOOTDIR/build/scp_task/bl301.bin $UBOOTDIR/fip/
cp $UBOOTDIR/build/board/hardkernel/odroidc4/firmware/acs.bin $UBOOTDIR/fip/
cp $UBOOTDIR/fip/g12a/bl2.bin $UBOOTDIR/fip/
cp $UBOOTDIR/fip/g12a/bl30.bin $UBOOTDIR/fip/
cp $UBOOTDIR/fip/g12a/bl31.img $UBOOTDIR/fip/
cp $UBOOTDIR/fip/g12a/ddr3_1d.fw $UBOOTDIR/fip/
cp $UBOOTDIR/fip/g12a/ddr4_1d.fw $UBOOTDIR/fip/
cp $UBOOTDIR/fip/g12a/ddr4_2d.fw $UBOOTDIR/fip/
cp $UBOOTDIR/fip/g12a/diag_lpddr4.fw $UBOOTDIR/fip/
cp $UBOOTDIR/fip/g12a/lpddr3_1d.fw $UBOOTDIR/fip/
cp $UBOOTDIR/fip/g12a/lpddr4_1d.fw $UBOOTDIR/fip/
cp $UBOOTDIR/fip/g12a/lpddr4_2d.fw $UBOOTDIR/fip/
cp $UBOOTDIR/fip/g12a/piei.fw $UBOOTDIR/fip/
cp $UBOOTDIR/fip/g12a/aml_ddr.fw $UBOOTDIR/fip/
cp u-boot.bin $UBOOTDIR/fip/bl33.bin

i$UBOOTDIR/fip/blx_fix.sh \
    $UBOOTDIR/fip/bl30.bin \
    $UBOOTDIR/fip/zero_tmp \
    $UBOOTDIR/fip/bl30_zero.bin \
    $UBOOTDIR/fip/bl301.bin \
    $UBOOTDIR/fip/bl301_zero.bin \
    $UBOOTDIR/fip/bl30_new.bin \
    bl30

$UBOOTDIR/fip/blx_fix.sh \
    $UBOOTDIR/fip/bl2.bin \
    $UBOOTDIR/fip/zero_tmp \
    $UBOOTDIR/fip/bl2_zero.bin \
    $UBOOTDIR/fip/acs.bin \
    $UBOOTDIR/fip/bl21_zero.bin \
    $UBOOTDIR/fip/bl2_new.bin \
    bl2

qemu-x86_64-static $UBOOTDIR/fip/g12a/aml_encrypt_g12a --bl30sig --input $UBOOTDIR/fip/bl30_new.bin \
                                    --output $UBOOTDIR/fip/bl30_new.bin.g12a.enc \
                                    --level v3
qemu-x86_64-static $UBOOTDIR/fip/g12a/aml_encrypt_g12a --bl3sig --input $UBOOTDIR/fip/bl30_new.bin.g12a.enc \
                                    --output $UBOOTDIR/fip/bl30_new.bin.enc \
                                    --level v3 --type bl30
qemu-x86_64-static $UBOOTDIR/fip/g12a/aml_encrypt_g12a --bl3sig --input $UBOOTDIR/fip/bl31.img \
                                    --output $UBOOTDIR/fip/bl31.img.enc \
                                    --level v3 --type bl31
qemu-x86_64-static $UBOOTDIR/fip/g12a/aml_encrypt_g12a --bl3sig --input $UBOOTDIR/fip/bl33.bin --compress lz4 \
                                    --output $UBOOTDIR/fip/bl33.bin.enc \
                                    --level v3 --type bl33 --compress lz4
qemu-x86_64-static $UBOOTDIR/fip/g12a/aml_encrypt_g12a --bl2sig --input $UBOOTDIR/fip/bl2_new.bin \
                                    --output $UBOOTDIR/fip/bl2.n.bin.sig
qemu-x86_64-static $UBOOTDIR/fip/g12a/aml_encrypt_g12a --bootmk \
            --output $UBOOTDIR/fip/u-boot.bin \
            --bl2 $UBOOTDIR/fip/bl2.n.bin.sig \
            --bl30 $UBOOTDIR/fip/bl30_new.bin.enc \
            --bl31 $UBOOTDIR/fip/bl31.img.enc \
            --bl33 $UBOOTDIR/fip/bl33.bin.enc \
            --ddrfw1 $UBOOTDIR/fip/ddr4_1d.fw \
            --ddrfw2 $UBOOTDIR/fip/ddr4_2d.fw \
            --ddrfw3 $UBOOTDIR/fip/ddr3_1d.fw \
            --ddrfw4 $UBOOTDIR/fip/piei.fw \
            --ddrfw5 $UBOOTDIR/fip/lpddr4_1d.fw \
            --ddrfw6 $UBOOTDIR/fip/lpddr4_2d.fw \
            --ddrfw7 $UBOOTDIR/fip/diag_lpddr4.fw \
            --ddrfw8 $UBOOTDIR/fip/aml_ddr.fw \
            --ddrfw9 $UBOOTDIR/fip/lpddr3_1d.fw \
            --level v3

# Does only copy the u-boot binary to ouput target, copying u-boot parts to the right sectors
# is done in board image definition (because an image could use somthing else than u-boot)
cp $UBOOTDIR/fip/u-boot.bin.sd.bin $1/$OUTPUT
