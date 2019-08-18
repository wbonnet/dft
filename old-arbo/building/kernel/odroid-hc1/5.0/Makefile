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
KERNEL_VERSION=5.0
KERNEL_FILE_VERSION=5.0

# Include board specific definitions
include ../board.mk

# Move sources directory to the correct name since it does not include full
# version in its naming
post-extract:
	@if [ ! -d "./$(NEW_VERSION)" ] ; then \
	mv $(EXTRACT_DIR)/$(SOFTWARE_UPSTREAM_NAME)-$(KERNEL_FILE_VERSION) $(WORK_SRC) ; \
        fi ;
	$(TARGET_DONE)

# Include build system
include buildsystem/dft.mk
