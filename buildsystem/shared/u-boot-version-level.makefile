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

# Include board specific definitions
include ../board.mk

# 
# u-boot version generic Makefile
#
# WARNING if you need to make any version specific modification or definition,
# Please take in consideration that you must not modify the content of this file.
# Otherwise it would modify the symlink target and become the new default value
# for all unmodified makefiles of all existing boards.

# Defines the version of the u-boot software
SW_VERSION   = $(notdir $(patsubst %/,%,$(shell pwd)))

# Defines patches to apply to the upstream sources :
# PATCHFILES += 0000_some_patch.diff

# If you use the patch feature, please make a copy of this file to store
# the definition of the PATCHFILES variable. The previous line in comment is
# provided as an example of how to do it. Please duplicate, modify and 
# uncomment the line. Files will be searched for in the files/ directory at
# the same level as this Makefile.  

# Include build system
include buildsystem/dft.u-boot.mk

# No need to recurse check target at version level
check :
	@echo "Checking folder containing '$(BOARD_NAME)' u-boot packaging procedure for version $(SW_VERSION)" 
	@if [ ! -f "../board.mk" ] ; then \
		echo "file board.mk is missing in directory $(shell pwd)/.." ; \
		false ; \
	fi ;
	@if [ ! -d "./files" ] ; then \
		echo "files directory is missing in $(shell pwd). It should contains the markdown file install.$(SRC_NAME).$(BOARD_NAME).md needed by target package." ; \
		false ; \
	fi ;
	@if [ ! -d "./debian" ] ; then \
		echo "debian directory is missing in $(shell pwd). It should contains the files needed to create the debian package for $(BOARD_NAME) u-boot." ; \
		false ; \
	fi ;
	@if [ ! -f "./files/install.$(SRC_NAME).$(BOARD_NAME).md" ] ; then \
		echo "markdown file install.$(SRC_NAME).$(BOARD_NAME).md describing the installation procedure is missing in directory $(shell pwd)/files. This file is needed by target package." ; \
		false ; \
	fi ;
	@if [ ! -L "./Makefile" ] ; then \
		echo "Makefile symlink to ../../../../../buildsystem/shared/u-boot-version-level.makefile is missing in $(shell pwd). You are using your own custom Makefile." ; \
		false ; \
	fi ; 
	@if [ ! -L "./buildsystem" ] ; then \
		echo "buildsystem symlink to ../../../../../buildsystem is missing in $(shell pwd). You are using your own custom buildsystem." ; \
		false ; \
	fi ;
	
help :
	@echo "Available targets"
	@echo 'check : Check folder content consistency. Report missing mandatory items (files, symlinks or direcories)'
