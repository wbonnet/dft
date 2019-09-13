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
UBOOT_VERSION     = $(notdir $(patsubst %/,%,$(shell pwd)))
GIT_BRANCH        = v$(UBOOT_VERSION)

# Include board specific definitions
include ../board.mk

# Defines patches to apply to the upstream sources :
# PATCHFILES += 0000_some_patch.diff

# If you use this patche feature please make a copy of this file to store 
# version specific list of patches. You should not modify the target of the link, 
# otherwise it would then behave as new default value for all unmodified versions 
# of all existing boards.

# Include build system
include buildsystem/dft.u-boot.mk
include buildsystem/dft.mk
