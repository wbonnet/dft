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

buildsystem := ../../../../buildsystem
include $(buildsystem)/dft.mk
include ./board.mk

# Do not recurse the following subdirs
MAKE_FILTERS = files Makefile README.md
SW_NAME      = SW_NAME_undefined_at_board_level

# ------------------------------------------------------------------------------
#
# Targets not associated with a file (aka PHONY)
#
.PHONY: help sanity-check

# Catch all target. Call the same targets in each subfolder
%:
	@echo "percent from board.makefile"
	@for i in $(filter-out $(MAKE_FILTERS),$(shell find . -mindepth 1 -maxdepth 1 -type d )) ; do \
		if [ -f $$i/Makefile ] ; then \
                $(MAKE) -C $$i $* || exit 1 ; \
		fi ; \
        done

sanity-check:
	@echo "sanity-check from board.makefile" ;
	echo "Checking board definition sanity for $(BOARD_NAME)" ;
	$(call dft_error) 
	echo "plop after call dft_error from board.makefile for $(BOARD_NAME)" ;
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
		echo "defconfig directory is missing in $(shell pwd)/kernel. It is used to store kernel configuration files. It should at least contain a hidden empty file .gitkeep until first kernel version is added for $(BOARD_NAME)" ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir -p $(shell pwd)/kernel/defconfig" ; \
		echo "touch $(shell pwd)/kernel/defconfig/.gitkeep" ; \
		echo "git add $(shell pwd)/kernel/defconfig" ; \
		echo "error 191114-03" ; \
		exit 1 ; \
	fi ;
	@if [ ! -d "$(shell pwd)/u-boot/files" ] ; then \
		echo "files directory is missing in $(shell pwd)/u-boot. It is used to store u-boot installation procedures. It should at least contain a hidden empty file .gitkeep until first uboot version is added for $(BOARD_NAME)" ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir -p $(shell pwd)/u-boot/files" ; \
		echo "touch $(shell pwd)/u-boot/files/.gitkeep" ; \
		echo "git add $(shell pwd)/u-boot/files" ; \
		echo "error 191117-01" ; \
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
		$(call dft_error "error 191114-02") \
		exit 1 ; \
	fi ;
	@if [ ! -L "kernel/board.mk" ] ; then \
		echo "board.mk symlink to ../board.mk is missing in directory $(shell pwd)/kernel" ; \
		echo "You can fix with the following commands : " ; \
		if [  -f "kernel/board.mk" ] ; then \
			echo "git rm $(shell pwd)/kernel/board.mk" ; \
		fi ; \
		echo "ln -s ../board.mk $(shell pwd)/kernel/board.mk" ; \
		echo "git add $(shell pwd)/kernel/board.mk" ; \
		echo "error 1911118-01" ; \
		exit 1 ; \
	fi ;
	@if [ ! "$(shell readlink kernel/board.mk)" = "../board.mk" ] ; then \
		echo "target of symlink board.mk should be ../board.mk in directory $(shell pwd)/kernel" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f $(shell pwd)/kernel/board.mk" ; \
		echo "ln -s ../board.mk $(shell pwd)/kernel/board.mk" ; \
		echo "git add $(shell pwd)/kernel/board.mk" ; \
		echo "error 1911118-02" ; \
		exit 1 ; \
	fi ;
	@if [ ! -L "u-boot/board.mk" ] ; then \
		echo "board.mk symlink to ../board.mk is missing in directory $(shell pwd)/u-boot" ; \
		echo "You can fix with the following commands : " ; \
		if [  -f "u-boot/board.mk" ] ; then \
			echo "git rm $(shell pwd)/u-boot/board.mk" ; \
		fi ; \
		echo "ln -s ../board.mk $(shell pwd)/u-boot/board.mk" ; \
		echo "git add $(shell pwd)/u-boot/board.mk" ; \
		echo "error 1911118-03" ; \
		exit 1 ; \
	fi ;
	@if [ ! "$(shell readlink u-boot/board.mk)" = "../board.mk" ] ; then \
		echo "target of symlink board.mk should be ../board.mk in directory $(shell pwd)/u-boot" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f $(shell pwd)/u-boot/board.mk" ; \
		echo "ln -s ../board.mk $(shell pwd)/u-boot/board.mk" ; \
		echo "git add $(shell pwd)/u-boot/board.mk" ; \
		echo "error 1911118-04" ; \
		exit 1 ; \
	fi ;
	@make -C u-boot sanity-check
	@make -C kernel sanity-check
	@for version in $(find . -mindepth 1 -maxdepth 1 -type d ) ; do \
		if [ -f $$version/Makefile ] ; then \
                $(MAKE) -C $$version $* || exit 1 ; \
		fi ; \
        done

# Build only u-boot  package target
u-boot-package:
	@echo "u-boot-package from board.makefile" ;
	$(MAKE) -C u-boot package || exit 1 ;

# Build only linux kernel an package target
kernel-package:
	@echo "kernel-package from board.makefile" ;
	$(MAKE) -C kernel package || exit 1 ;
