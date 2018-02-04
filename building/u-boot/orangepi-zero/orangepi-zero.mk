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
# Copyright 2016 DFT project (http://www.debianfirmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#

# Defines board name
BOARD_NAME = orangepi-zero
BOARD_ARCH = armhf

# Defines the git repository to use
KERNEL_GIT_URL         = https://github.com/u-boot
KERNEL_GIT_REPO        = u-boot

# Set config file to empty and define the name of the board to use a defconfig
USE_CONFIG_FILE        =
USE_DEFCONFIG          = orangepi_zero_defconfig

# Defines the list of files to copy (path is relative to build dir)
UBOOT_BINARY_FILE      = u-boot-sunxi-with-spl.bin

