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
SW_VERSION      = $(notdir $(patsubst %/,%,$(shell pwd)))

# Retrieve th builder hot architecure if not defined yet
HOST_ARCH      ?= $(shell uname -m)

# Include board specific definitions
include ../board.mk

# Defines patches to apply to the upstream sources :
# PATCHFILES += 0000_some_patch.diff

# If you use this patche feature please make a copy of this file to store 
# version specific list of patches. You should not modify the target of the link, 
# otherwise it would then behave as new default value for all unmodified versions 
# of all existing boards.

# Include build system
include buildsystem/dft.kernel.mk

# Catch all target. Call the same targets in each subfolder
%:
	@if [ ! "x$(HOST_ARCH)" = "x$(BOARD_ARCH)" ] ; \
	then \
	    echo "Board is $(BOARD_ARCH) and i run on $(HOST_ARCH). Skipping recursive target call..." ; \
	    echo "Cross compilation is not yet supported by DFT. Please don't hesitate to contact the team if it is really blocking." ; \
	    true ; \
	else \
		for i in $(filter-out $(FILTER_DIRS),$(wildcard */)) ; do \
			$(MAKE) -C $$i $* || exit 1 ; \
		done \
	fi

# ------------------------------------------------------------------------------
#
# Target that prints the help
#
help :
	@echo "Available targets are :" ; \
	echo '   not the good help' ;
