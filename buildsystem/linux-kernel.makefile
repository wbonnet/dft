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
#	William Bonnet	 wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#

# Defines variables specific to Linux kernel
SW_NAME	= linux
SW_VERSION = SW_VERSION_undefined_at_kernel_level

$(info "D3BUG linux-kernel.makefile")
buildsystem := ../../../../buildsystem
include board.mk
include $(buildsystem)/inc/linux-kernel.mk
include $(buildsystem)/dft.mk

# Do not recurse the following subdirs
MAKE_FILTERS  = files defconfig Makefile README.md .

# 
# Board level birectory generic Linux kernel makefile
#

sanity-check :
	@echo "Checking Linux kernel folder sanity for board $(BOARD_NAME)" 
	@if [ ! -L "Makefile"  ] ; then \
		echo "Makefile symlink $(buildsystem)/$(SW_NAME)-kernel.makefile is missing in directory $(shell pwd)" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f $(shell pwd)/Makefile" ; \
		echo "ln -s $(buildsystem)/$(SW_NAME)-kernel.makefile $(shell pwd)/Makefile" ; \
		echo "git add $(shell pwd)/Makefile" ; \
		echo "error 191121-010" ; \
		exit 1 ; \
	fi ;
	@if [ ! "$(shell readlink ./Makefile)" = "$(buildsystem)/$(SW_NAME)-kernel.makefile" ] ; then \
		echo "target of symlink Makefile should be $(buildsystem)/$(SW_NAME)-kernel.makefile in directory $(shell pwd)" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f $(shell pwd)/Makefile" ; \
		echo "ln -s $(buildsystem)/$(SW_NAME)-kernel.makefile $(shell pwd)/Makefile" ; \
		echo "git add $(shell pwd)/Makefile" ; \
		echo "error 1911120-011" ; \
		exit 1 ; \
	fi ;
	@if [ ! -d "$(shell pwd)/defconfig" ] ; then \
		echo "defconfig directory is missing in $(shell pwd). It contains the configuration files of the different Linux kernel versions." ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir -p $(shell pwd)/defconfig" ; \
		echo "touch $(shell pwd)/defconfig/.gitkeep" ; \
		echo "git add $(shell pwd)/defconfig/.gitkeep" ; \
		echo "error 191120-013" ; \
 		exit 1 ; \
	fi ;
	@if [ ! -L "board.mk" ] ; then \
		echo "board.mk symlink to ../board.mk is missing in directory $(shell pwd)" ; \
		echo "You can fix with the following commands : " ; \
		echo "ln -s ../board.mk $(shell pwd)/board.mk" ; \
		echo "git add $(shell pwd)/board.mk" ; \
		echo "error 1911116-04" ; \
		exit 1 ; \
	fi ;
	@if [ ! "$(shell readlink board.mk)" = "../board.mk" ] ; then \
		echo "target of symlink board.mk should be ../board.mk in directory $(shell pwd)" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f $(shell pwd)/board.mk" ; \
		echo "ln -s ../board.mk $(shell pwd)/board.mk" ; \
		echo "git add $(shell pwd)/board.mk" ; \
		echo "error 1911116-05" ; \
		exit 1 ; \
	fi ;
	@for version in $(shell find . -mindepth 1 -maxdepth 1 -type d  -name '*\.*' ) ; do \
		echo "checking version $$version subfolder" ; \
		if [ ! -L "$$version/Makefile" ] ; then \
			echo "version folder $$version" ; \
			echo "Makefile symlink in $(shell pwd)/$$version is missing. It should be a symlink to $(buildsystem)/linux-kernel-version.makefile" ; \
			echo "You can fix with the following shell commands :" ; \
			if [ -f "$$version/Makefile" ] ; then \
				echo "git rm $$version/Makefile" ; \
			fi ; \
			echo "ln -s ../$(buildsystem)/linux-kernel-version.makefile $$version/Makefile" ; \
			echo "git add $$version/Makefile" ; \
			echo "exit 191116-07" ; \
			exit 1 ; \
		fi ; \
		s=`readlink $$version/Makefile` ; \
		if [ !  "$$s" = "../$(buildsystem)/linux-kernel-version.makefile" ] ; then \
			echo "Makefile symlink in $$version must link to $(buildsystem)/linux-kernel-version.makefile" ; \
			echo "You can fix with the following shell commands :" ; \
			echo "git rm -f $$version/Makefile || rm -f $$version/Makefile" ; \
			echo "ln -s ../$(buildsystem)/linu-kernel-version.makefile $$version/Makefile" ; \
			echo "git add $$version/Makefile" ; \
			echo "exit 191115-09" ; \
			exit 1 ; \
		fi ; \
	done ; 
	@for folder in $(shell find . -mindepth 1 -maxdepth 1 -type d -name '*\.*') ; do \
		$(MAKE) -C $$folder sanity-check || exit 1 ; \
		echo "make sanity-check in u-boot version $$folder" ; \
	done ;

# Catch all target. Call the same targets in each subfolder
%:
	for f in $(filter-out $(MAKE_FILTERS),$(shell find . -mindepth 1 -maxdepth 1 -type d )) ; do \
		$(MAKE) -C $$f $* || exit 1 ; \
	done

help :
	@echo "Supported targets are"
	@echo 'sanity-check : Verify the availability of required items (files, symlinks, directories) and report missing.'
