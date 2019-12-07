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

# Defines the kernel version
UBOOT_VERSION      = 2018.01
KERNEL_GIT_BRANCH  = v$(UBOOT_VERSION)

# Include board specific definitions
include ../board.mk

# Defines the patches to apply on the sources
# PATCHFILES += 0000_some_patch.diff

# Include build system
include buildsystem/dft.u-boot.mk
