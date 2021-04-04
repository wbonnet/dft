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
# Copyright 2016 DFT project (http://www.firmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#

#
# Board global parameters
#

# The board name fragment will be used in package naming, path and files content generation
BOARD_NAME = sun-sparc64

# Board architecture as defined by uname -m (armv7l, mips, aarch64, x86_64, etc.)
BOARD_ARCH = sparc64



#
# u-boot support and configuration
#

# Defines if u-boot should be generated (set UBOOT_SUPPORT to 1) (0 means u-boot is not available).
# if UBOOT_SUPPORT is disabled packaging is skipped. In this case, you may have to activate GRUB.
UBOOT_SUPPORT = r0

# Make use the defconfig file from UBOOT_DEFCONFIG unless you specify your own in USE_CONFIG_FILE
# UBOOT_DEFCONFIG = orangepi_zero_defconfig

# List of files to copy from build to install directory (path is relative to build dir)
# UBOOT_BINARY_FILE = u-boot-sunxi-with-spl.bin
D# EFAULT_DTB = sun8i-h2-plus-orangepi-zero.dtb


#
# GRUB support and configuration (u-boot or grub should be activated to be able to boot the board)
#
GRUB_SUPPORT = 1


#
# Linux Kernel  support and configuration
#

# Should the Linux Kernel be generated (set LINUX_KERNEL_SUPPORT to 1) (0 means do not generate linux kernel)
# if LINUX_KERNEL_SUPPORT is disabled packaging is skipped. In this case, you will have to activate an alternate kernel
LINUX_KERNEL_SUPPORT = 1

# Defines the board specific kernel config files. Other defconfig files are layers applied on top of this one
LINUX_KERNEL_BOARD_BLUEPRINT ?= $(BOARD_NAME).defconfig



#defconfig communs
#defconfig overlays list
#/home/william/workspace/dft/bsp-packages/linux-kernel-fragments/hardware/mutual/
#pour le moment ya rien
#/home/william/workspace/dft/bsp-packages/linux-kernel-fragments/hardware/board-blueprints/
#la j'ai board-name.defconfig

#/home/william/workspace/dft/bsp-packages/linux-kernel-fragments/hardware/device-drivers/
#+=usb/plop.defconfig
#/home/william/workspace/dft/bsp-packages/linux-kernel-fragments/functional/
#+= containers/
#config_cgroups.config
#config_ns.cfg
#security/security.USE_CONFIG_FILE
#c du fonctionel

# Make use the defconfig file from UBOOT_DEFCONFIG unless you specify your own in USE_CONFIG_FILE
# UBOOT_DEFCONFIG = orangepi_zero_defconfig

# List of files to copy from build to install directory (path is relative to build dir)
# UBOOT_BINARY_FILE = u-boot-sunxi-with-spl.bin
# DEFAULT_DTB = sun8i-h2-plus-orangepi-zero.dtb

