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

# Defines variables specific to Linux kernel
SW_NAME     = linux
SW_VERSION  = $(notdir $(patsubst %/,%,$(shell pwd)))


$(info "D3BUG linux-kernel-version.makefile")
buildsystem := ../../../../../buildsystem
include ../board.mk
include $(buildsystem)/inc/linux-kernel.mk
include $(buildsystem)/dft.mk
$(warning "review in progress linux-kernel-version.makefile")

# Defines the kernel version
SW_VERSION      = $(notdir $(patsubst %/,%,$(shell pwd)))

# Retrieve th builder hot architecure if not defined yet
HOST_ARCH      ?= $(shell uname -m)

# Do not recurse the following subdirs
MAKE_FILTERS  = Makefile README.md .

# Include board specific definitions
include ../board.mk

# Defines patches to apply to the upstream sources :
# PATCHFILES += 0000_some_patch.diff

# If you use this patche feature please make a copy of this file to store 
# version specific list of patches. You should not modify the target of the link, 
# otherwise it would then behave as new default value for all unmodified versions 
# of all existing boards.

# Include build system
$(warning " FIXME hardi coded path")
include buildsystem/inc/linux-kernel.mk

# No need to recurse check target at version level
check :
	@echo "Checking $(SW_NAME) kernel package definition version $(SW_VERSION) for $(BOARD_NAME)"
	@if [ ! -f "../board.mk" ] ; then \
		echo "file board.mk is missing in directory $(shell pwd)/.." ; \
		false ; \
	fi ;
	@if [ ! -d "../defconfig" ] ; then \
		echo "kernel config files directory is missing $(shell pwd)/../defconfig" ; \
		false ; \
	fi ;
	@if [ ! -d "./debian" ] ; then \
		echo "debian directory is missing in $(shell pwd). It should contains the files needed to create the debian package for $(BOARD_NAME) u-boot." ; \
		false ; \
	fi ;
	@if [ ! -L "./Makefile" ] ; then \
		echo "Makefile symlink to ../../../../../buildsystem/linux-kernel-version.makefile is missing in $(shell pwd). You are using your own custom Makefile." ; \
		false ; \
	fi ;
	@if [ ! -L "./buildsystem" ] ; then \
		echo "buildsystem symlink to ../../../../../buildsystem is missing in $(shell pwd). You are using your own custom buildsystem." ; \
		false ; \
	fi ;
	@if [ ! "$(shell readlink ./Makefile)" = "../../../../../buildsystem/linux-kernel-version.makefile" ] ; then \
		echo "target of symlink Makefile should be ../../../../../buildsystem/linux-kernel-version.makefile in directory $(shell pwd). You are using your own custom buildsystem." ; \
		false ; \
	fi ;
	@if [ ! "$(shell readlink ./buildsystem)" = "../../../../../buildsystem" ] ; then \
		echo "target of symlink buildsystem should be ../../../../../buildsystem in directory $(shell pwd). You are using your own custom buildsystem." ; \
		false ; \
	fi ;

help :
	@echo "Supported targets are"
	@echo 'check : Verify the availability of required items (files, symlinks, directories) and report missing.'

