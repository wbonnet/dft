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

$(info "D3BUG board.makefile")
buildsystem := ../../../../buildsystem
include $(buildsystem)/dft.mk
include board.mk
$(warning "review in progress board.makefile")

# Do not recurse the following subdirs
MAKE_FILTERS  = Makefile README.md
SRC_NAME      = not_defined_at_kernel_level_must_go_into_version_subdir

# ------------------------------------------------------------------------------
#
# Targets not associated with a file (aka PHONY)
#
.PHONY: help check

# 
# Board level generic Makefile
#

# board level directory must contain board.mk file, kernel folder and u-boot folder
check :
# Mandatory folders content check (otherwise recusive targets may not work)

# Board level directory must contain board.mk file, kernel folder and u-boot folder
	@echo "Checking board definition for $(BOARD_NAME)" ;
	@if [ ! -f "board.mk" ] ; then \
		pwd ; \
		echo "file board.mk is missing in directory $(shell pwd)" ; \
		echo "error 191112-01" ; \
		exit 1 ; \
	fi ;
	@if [ ! -d "$(shell pwd)/kernel" ] ; then \
		echo "kernel directory is missing in $(shell pwd). It should contains a symlink to the generic makefile for Linux kernel" ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir -p $(shell pwd)/kernel" ; \
		echo "ln -s $(buildsystem)/linux-kernel.makefile $(shell pwd)/kernel/Makefile" ; \
		echo "git add $(shell pwd)/kernel" ; \
		echo "error 191114-01" ; \
		exit 1 ; \
	fi ;
	@if [ ! -d "$(shell pwd)/kernel/defconfig" ] ; then \
		echo "defconfig directory is missing in $(shell pwd). It is used to store kernel configuration files. It should at leasty contains a hidden empty file .gitkeep until first kernel version is added" ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir -p $(shell pwd)/kernel/defconfig" ; \
		echo "touch $(shell pwd)/kernel/defconfig/.gitkeep" ; \
		echo "git add $(shell pwd)/kernel/defconfig" ; \
		echo "error 191114-03" ; \
		exit 1 ; \
	fi ;
	@if [ ! -d "$(shell pwd)/u-boot" ] ; then \
		echo "u-boot directory is missing in $(shell pwd). It should contains a symlink to the generic makefile for u-boot" ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir -p $(shell pwd)/u-boot" ; \
		echo "ln -s $(buildsystem)/u-boot.makefile $(shell pwd)/u-boot/Makefile" ; \
		echo "git add $(shell pwd)/u-boot" ; \
		echo "error 191114-02" ; \
		exit 1 ; \
	fi ;
	@if [ ! -d "$(shell pwd)/files" ] ; then \
		echo "files directory is missing in $(shell pwd). It should contains the markdown file install.$(SRC_NAME).$(BOARD_NAME).md needed by target package." ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir -p $(shell pwd)/files" ; \
		echo "touch $(shell pwd)/files/.gitkeep" ; \
		echo "ln -s ../../files/install.$(SRC_NAME).$(BOARD_NAME).md $(shell pwd)/files/" ; \
		echo "git add $(shell pwd)/files" ; \
		echo "error 191112-02" ; \
		exit 1 ; \
	fi ;
	@if [ ! -e "$(shell readlink files/install.$(SRC_NAME).$(BOARD_NAME).md)" ] ; then \
		echo "the target of installation procedure in files is missing.  It should link to the markdown file install.$(SRC_NAME).$(BOARD_NAME).md needed by target package." ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f $(shell pwd)/files/install.$(SRC_NAME).$(BOARD_NAME).md" ; \
		echo "ln -s ../../files/install.$(SRC_NAME).$(BOARD_NAME).md $(shell pwd)/files/" ; \
		echo "mkdir -p $(shell pwd)/files" ; \
		echo "git add $(shell pwd)/files/$(SRC_NAME).$(BOARD_NAME).md" ; \
		echo "error 191116-01" ; \
		exit 1 ; \
	fi ;
	@if [ ! "$(shell readlink u-boot/Makefile)" = "$(buildsystem)/u-boot.makefile" ] ; then \
		echo "target of symlink Makefile should be $(buildsystem)/u-boot.makefile in directory $(shell pwd)/u-boot" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f $(shell pwd)/u-boot/Makefile" ; \
		echo "mkdir -p $(shell pwd)/u-boot" ; \
		echo "ln -s $(buildsystem)/u-boot.makefile $(shell pwd)/u-boot/Makefile" ; \
		echo "git add $(shell pwd)/u-boot/Makefile" ; \
		echo "error 191114-01" ; \
		exit 1 ; \
	fi ;
	@if [ ! "$(shell readlink kernel/Makefile)" = "$(buildsystem)/linux-kernel.makefile" ] ; then \
		echo "target of symlink Makefile should be $(buildsystem)/linux-kernel.makefile in directory $(shell pwd)/kernel" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f $(shell pwd)/kernel/Makefile" ; \
		echo "mkdir -p $(shell pwd)/kernel" ; \
		echo "ln -s $(buildsystem)/linux-kernel.makefile $(shell pwd)/kernel/Makefile" ; \
		echo "git add $(shell pwd)/kernel/Makefile" ; \
		echo "error 191114-02" ; \
		exit 1 ; \
	fi ;

# Catch all target. Call the same targets in each subfolder
%:
	@for i in $(filter-out $(MAKE_FILTERS),$(shell find . -mindepth 1 -maxdepth 1 -type d )) ; do \
                $(MAKE) -C $$i $* || exit 1 ; \
        done


help :
	@echo "Supported targets are"
	@echo 'check : Verify the availability of required items (files, symlinks, directories) and report missing.'
