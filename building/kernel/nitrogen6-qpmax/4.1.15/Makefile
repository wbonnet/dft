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
 
# Defines the kernel version
KERNEL_VERSION=4.1.15

# Include board specific definitions
include ../board.mk

# Defines the patches to apply on the sources
# PATCHFILES += 0000_some_patch.diff

# Activate git download method
UPSTREAM_DOWNLOAD_TOOL = git

# Upstream git server
KERNEL_GIT_URL    = https://github.com/boundarydevices
KERNEL_GIT_REPO   = linux-imx6
KERNEL_GIT_BRANCH = boundary-imx_4.1.15_2.0.0_ga

# Uncomment to recreate the config file. Otherwise confif from fileS/is used
# USE_DEFCONFIG     = boundary_defconfig
# USE_CONFIG_FILE   =

# Include build system
include buildsystem/dft.mk
