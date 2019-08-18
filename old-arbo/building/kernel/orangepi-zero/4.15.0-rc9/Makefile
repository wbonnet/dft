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
KERNEL_VERSION=4.15.0-rc9
KERNEL_FILE_VERSION=4.15-rc9

# Move sources directory to the correct name since it does not include full
# version in its naming
post-extract:
	@mv $(EXTRACT_DIR)/$(SOFTWARE_UPSTREAM_NAME)-$(KERNEL_FILE_VERSION) $(WORK_SRC)
	$(TARGET_DONE)

# Include board specific definitions
include ../board.mk

# Defines the patches to apply on the sources
# PATCHFILES += 0000_some_patch.diff

SOFTWARE_UPSTREAM_SITES = http://git.kernel.org/torvalds/t/
SOFTWARE_DIST_FILES     = $(SOFTWARE_UPSTREAM_NAME)-$(KERNEL_FILE_VERSION).tar.gz

# Include build system
include buildsystem/dft.mk
