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

# Defines variables specific to u-boot
SW_NAME   = u-boot

$(info "D3BUG u-boot-version.makefile")
buildsystem := ../../../../../buildsystem
include $(buildsystem)/inc/dft.u-boot.mk
include $(buildsystem)/dft.mk

# Include board specific definitions  from board level
include ../board.mk

# u-boot version generic Makefile
#
# WARNING if you need to make any version specific modification or definition,
# Please take in consideration that you must not modify the content of this file.
# Otherwise it would modify the symlink target and become the new default value
# for all unmodified makefiles of all existing boards.

# Defines patches to apply to the upstream sources :
# PATCHFILES += 0000_some_patch.diff

# If you use the patch feature, please make a copy of this file to store
# the definition of the PATCHFILES variable. The previous line in comment is
# provided as an example of how to do it. Please duplicate, modify and 
# uncomment the line. Files will be searched for in the files/ directory at
# the same level as this Makefile.  

# Do not recurse the following subdirs
MAKE_FILTERS  = debian files patches

# ------------------------------------------------------------------------------
#
# Targets not associated with a file (aka PHONY)
#
.PHONY:

help:
	@echo "Supported targets are"
	@echo 'check : Verify the availability of required items (files, symlinks, directories) and report missing.'

check:
	@echo "Checking u-boot version $(SW_VERSION) package definition for $(BOARD_NAME)" 
	@if [ ! -f "../board.mk" ] ; then \
		echo "file board.mk is missing in directory $(shell pwd)/.." ; \
		echo "error 191115-12" ; \
		exit 1 ; \
	fi ;
	@if [ ! -d "$(shell pwd)/files" ] ; then \
		echo "files directory is missing in $(shell pwd). It should contains the markdown file install.$(SW_NAME).$(BOARD_NAME).md needed by target package." ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir -p $(shell pwd)/files" ; \
		echo "ln -s ../../files/install.$(SW_NAME).$(BOARD_NAME).md $(shell pwd)/files/" ; \
		echo "error 191115-11" ; \
		exit 1 ; \
	fi ;
	@if [ ! -d "$(shell pwd)/debian" ] ; then \
		echo "debian directory is missing in $(shell pwd). It should contains the files needed to create the debian package for $(BOARD_NAME) u-boot." ; \
		echo "error 191115-10" ; \
		exit 1 ; \
	fi ;

# Catch all target. Call the same targets in each subfolder
muf:
	exit 1 ; 
	for version in $(shell find . -mindepth 1 -maxdepth 1 -type d ) ; do \
		if [ "$$version" = "./patches"  ] ; then \
			continue ; \
		fi ; \
		if [ "$$version" = "./files" ] ; then \
			continue ; \
		fi ; \
		if [ "$$version" = "./debian" ] ; then \
			continue ; \
		fi ; \
		$(MAKE) -C $$version $* || exit 1 ; \
	done
