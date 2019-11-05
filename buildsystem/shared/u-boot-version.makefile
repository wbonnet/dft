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
	@echo "Checking u-boot version $(SW_VERSION) package definition for $(BOARD_NAME)" 
	@if [ ! -f "../board.mk" ] ; then \
		echo "file board.mk is missing in directory $(shell pwd)/.." ; \
		false ; \
	fi ;
	@if [ ! -d "$(shell pwd)/files" ] ; then \
		echo "files directory is missing in $(shell pwd). It should contains the markdown file install.$(SRC_NAME).$(BOARD_NAME).md needed by target package." ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir $(shell pwd)/files" ; \
		echo "ln -s ../../files/install.$(SRC_NAME).$(BOARD_NAME).md $(shell pwd)/files/" ; \
		false ; \
	fi ;
	@if [ ! -d "./debian" ] ; then \
		echo "debian directory is missing in $(shell pwd). It should contains the files needed to create the debian package for $(BOARD_NAME) u-boot." ; \
		false ; \
	fi ;
	@if [ ! -L "files/install.$(SRC_NAME).$(BOARD_NAME).md" ] ; then \
		echo "Installation procedure symlink is missing under $(shell pwd)/files" ; \
		echo "This folder should contain a symlink to the markdown file describing u-boot installation produre for $(BOARD_NAME)" ; \
		echo "You can fix with the following commands : " ; \
		echo "ln -s ../../files/install.u-boot.$(BOARD_NAME).md $(shell pwd)/files/install.u-boot.$(BOARD_NAME).md" ; \
		echo "git add $(shell pwd)/files/install.u-boot.$(BOARD_NAME).md" ; \
		exit 1 ; \
	fi ;
	@if [ ! -L "./Makefile" ] ; then \
		echo "Makefile symlink to ../../../../../buildsystem/shared/u-boot-version.makefile is missing in $(shell pwd)" ; \
		false ; \
	fi ; 
	@if [ ! -L "./buildsystem" ] ; then \
		echo "buildsystem symlink to ../../../../../buildsystem is missing in $(shell pwd). You are using your own custom buildsystem" ; \
		false ; \
	fi ;
	@if [ ! "$(shell readlink ./buildsystem)" = "../../../../../buildsystem" ] ; then \
		echo "target of symlink buildsystem should be ../../../../../buildsystem in directory $(shell pwd)" ; \
		false ; \
	fi ;
	@if [ ! "$(shell readlink ./Makefile)" = "../../../../../buildsystem/shared/u-boot-version.makefile" ] ; then \
		echo "target of symlink Makefile should be ../../../../../buildsystem/shared/u-boot-version.makefile in directory $(shell pwd)" ; \
		false ; \
	fi ;
	
help :
	@echo "Supported targets are"
	@echo 'check : Verify the availability of required items (files, symlinks, directories) and report missing.'
