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
# Copyright 2016 DFT project (http://www.firmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#

# Build system sould be available under board folder as a symlink. Keep it
# locally available under board folder computing a relative path is a nightmare
# and does not work in all cases. Environment variables are not git friendly
# since git add will loose variable name and generate an absolute path, which
# is not comptible with user need ans or workspace relocation nor packagng needs.
# better solutions wille be really welcomeds contributions.
DFT_BUILDSYSTEM := buildsystem
include board.mk
include $(DFT_BUILDSYSTEM)/dft.mk

# Strip the variables defined in board.mk to remove trailing whitespaces or
# some calls will fail (when passing defconfig name etc.)
BOARD_NAME      := $(strip $(BOARD_NAME))
BOARD_ARCH      := $(strip $(BOARD_ARCH))
UBOOT_SUPPORT   := $(strip $(UBOOT_SUPPORT))
UBOOT_DEFCONFIG := $(strip $(UBOOT_DEFCONFIG))
USE_CONFIG_FILE := $(strip $(USE_CONFIG_FILE))

# Do not recurse the following subdirs
MAKE_FILTERS := kernel u-boot buildsystem files Makefile README.md

# ------------------------------------------------------------------------------
#
# Targets not associated with a file (aka PHONY)
#
.PHONY:

sanity-check: sanity-check-subdirs
	@if [ ! -f "board.mk" ] ; then \
		pwd ; \
		echo "file board.mk is missing in directory ${CURDIR}" ; \
	        $(call dft_error ,1911-1201) ; \
	fi ;
	@if [ ! -d "${CURDIR}/kernel" ] ; then \
		echo "kernel directory is missing in i${CURDIR}. It should contains a symlink to the generic makefile for Linux kernel" ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir -p ${CURDIR}/kernel" ; \
		echo "ln -s $(DFT_BUILDSYSTEM)/linux-kernel.makefile ${CURDIR}/kernel/Makefile" ; \
		echo "git add ${CURDIR}/kernel" ; \
	        $(call dft_error ,2001-0102) ; \
	fi ;
	@if [ ! -d "${CURDIR}/kernel/defconfig" ] ; then \
		echo "defconfig directory is missing in ${CURDIR}/kernel. It is used to store kernel configuration files. It should at least contain a hidden empty file .gitkeep until first kernel version is added for $(BOARD_NAME)" ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir -p ${CURDIR}/kernel/defconfig" ; \
		echo "touch ${CURDIR}/kernel/defconfig/.gitkeep" ; \
		echo "git add ${CURDIR}/kernel/defconfig" ; \
	        $(call dft_error ,1911-1403) ; \
	fi ;
	@if [ ! -d "${CURDIR}/u-boot/files" ] ; then \
		echo "files directory is missing in ${CURDIR}/u-boot. It is used to store u-boot installation procedures. It should at least contain a hidden empty file .gitkeep until first uboot version is added for $(BOARD_NAME)" ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir -p ${CURDIR}/u-boot/files" ; \
		echo "touch ${CURDIR}/u-boot/files/.gitkeep" ; \
		echo "git add ${CURDIR}/u-boot/files" ; \
	        $(call dft_error ,1911-1701) ; \
	fi ;
	@if [ ! -d "${CURDIR}/u-boot" ] ; then \
		echo "u-boot directory is missing in ${CURDIR}. It should contains a symlink to the generic makefile for u-boot" ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir -p ${CURDIR}/u-boot" ; \
		echo "ln -s $(DFT_BUILDSYSTEM)/u-boot.makefile ${CURDIR}/u-boot/Makefile" ; \
		echo "git add ${CURDIR}/u-boot" ; \
	        $(call dft_error ,1911-1402) ; \
	fi ;
	@if [ ! "$(shell readlink ${CURDIR}/u-boot/Makefile)" = "../$(DFT_BUILDSYSTEM)/u-boot.makefile" ] ; then \
		echo "target of symlink Makefile should be ../$(DFT_BUILDSYSTEM)/u-boot.makefile in directory ${CURDIR}/u-boot" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f ${CURDIR}/u-boot/Makefile" ; \
		echo "mkdir -p ${CURDIR}/u-boot" ; \
		echo "DFT_BUILDSYSTEM : ${DFT_BUILDSYSTEM}" ; \
		echo "ln -s ../$(DFT_BUILDSYSTEM)/u-boot.makefile ${CURDIR}/u-boot/Makefile" ; \
		echo "git add ${CURDIR}/u-boot/Makefile" ; \
	        $(call dft_error ,2001-0101) ; \
	fi ;
	@if [ ! "$(shell readlink ${CURDIR}/kernel/Makefile)" = "../$(DFT_BUILDSYSTEM)/linux-kernel.makefile" ] ; then \
		echo "target of symlink Makefile should be ../$(DFT_BUILDSYSTEM)/linux-kernel.makefile in directory ${CURDIR}/kernel" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f ${CURDIR}/kernel/Makefile" ; \
		echo "mkdir -p ${CURDIR}/kernel" ; \
		echo "ln -s ../$(DFT_BUILDSYSTEM)/linux-kernel.makefile ${CURDIR}/kernel/Makefile" ; \
		echo "git add ${CURDIR}/kernel/Makefile" ; \
		$(call dft_error 1911-1409) \
	fi ;
	@if [ ! -L "kernel/board.mk" ] ; then \
		echo "board.mk symlink to ../board.mk is missing in directory ${CURDIR}/kernel" ; \
		echo "You can fix with the following commands : " ; \
		if [  -f "kernel/board.mk" ] ; then \
			echo "git rm ${CURDIR}/kernel/board.mk" ; \
		fi ; \
		echo "ln -s ../board.mk ${CURDIR}/kernel/board.mk" ; \
		echo "git add ${CURDIR}/kernel/board.mk" ; \
	        $(call dft_error ,1911-1801) ; \
	fi ;
	@if [ ! "$(shell readlink ${CURDIR}/kernel/board.mk)" = "../board.mk" ] ; then \
		echo "target of symlink board.mk should be ../board.mk in directory ${CURDIR}/kernel" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f ${CURDIR}/kernel/board.mk" ; \
		echo "ln -s ../board.mk ${CURDIR}/kernel/board.mk" ; \
		echo "git add ${CURDIR}/kernel/board.mk" ; \
	        $(call dft_error ,1911-1802) ; \
	fi ;
	@if [ ! "" = "" ] ; then \
		echo "target of symlink board.mk should be ../board.mk in directory ${CURDIR}/kernel" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f ${CURDIR}/kernel/board.mk" ; \
		echo "ln -s ../board.mk ${CURDIR}/kernel/board.mk" ; \
		echo "git add ${CURDIR}/kernel/board.mk" ; \
	        $(call dft_error ,2001-0601) ; \
	fi ;
	@if [ ! -L "u-boot/board.mk" ] ; then \
		echo "board.mk symlink to ../board.mk is missing in directory ${CURDIR}/u-boot" ; \
		echo "You can fix with the following commands : " ; \
		if [  -f "u-boot/board.mk" ] ; then \
			echo "git rm ${CURDIR}/u-boot/board.mk" ; \
		fi ; \
		echo "ln -s ../board.mk ${CURDIR}/u-boot/board.mk" ; \
		echo "git add ${CURDIR}/u-boot/board.mk" ; \
	        $(call dft_error ,1911-1803) ; \
	fi ;
	@if [ ! "$(shell readlink ${CURDIR}/u-boot/board.mk)" = "../board.mk" ] ; then \
		echo "target of symlink board.mk should be ../board.mk in directory ${CURDIR}/u-boot" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f ${CURDIR}/u-boot/board.mk" ; \
		echo "ln -s ../board.mk ${CURDIR}/u-boot/board.mk" ; \
		echo "git add ${CURDIR}/u-boot/board.mk" ; \
	        $(call dft_error ,1911-1804) ; \
	fi ;
	@make --directory=u-boot $*
	@make --directory=kernel $*
	@for version in $(find . -mindepth 1 -maxdepth 1 -type d -printf '%P\n') ; do \
		$(MAKE) --directory=$$version $* only-native-arch=$(only-native-arch) arch-warning=$(arch-warning) verbority=$(verbosity) ; \
        done

u-boot-package:
	$(MAKE) --directory=u-boot package only-native-arch=$(only-native-arch) arch-warning=$(arch-warning) verbosity=$(verbosity);

# Build only linux kernel an package target
linux-kernel-package:
kernel-package:
	$(MAKE) --directory=kernel package only-native-arch=$(only-native-arch) arch-warning=$(arch-warning) verbosity=$(verbosity);

# Catch all target. Call the same targets in each subfolder
# cd $$i && $(MAKE) $* && cd .. ;
sanity-check-subdirs:
	@for i in $(filter-out $(MAKE_FILTERS),$(shell find . -mindepth 1 -maxdepth 1 -type d -printf '%P\n')) ; do \
		echo "examen de $$i" ; \
		if [ -f $$i/Makefile ] ; then \
			$(MAKE) --directory=$$i $* verbosity=$(verbosity); \
		fi ; \
        done

# Create a new u-boot version entry
add-u-boot-version:
	$(MAKE) --warn-undefined-variables --directory=u-boot add-u-boot-version new-version=$(new-version) ;

check-u-boot-defconfig:
	$(MAKE) --directory=u-boot check-u-boot-defconfig verbosity=$(verbosity);

# Simple forwarder
#post-setup extract fetch build configure:
post-setup:
	@for v in $(filter-out $(MAKE_FILTERS),$(shell find .  -mindepth 1 -maxdepth 1 -type d -printf '%P\n')) ; do \
		if [ -f ${CURDIR}/$$v/Makefile ] ; then \
                	$(MAKE) --directory=$$v $@ only-native-arch=$(only-native-arch) arch-warning=$(arch-warning); \
		fi ; \
	done

show-u-boot-dft-version-for:
	echo "BSB : je suis la 1" ;
	pwd ;
	for v in $(filter-out $(MAKE_FILTERS),$(shell find .  -mindepth 1 -maxdepth 1 -type d -printf '%P\n')) ; do \
		if [ -f ${CURDIR}/$$v/Makefile ] ; then \
                	$(MAKE) --directory=$$v $@ only-native-arch=$(only-native-arch) arch-warning=$(arch-warning); \
		fi ; \
	done

show-kernel-dft-version-for:
	echo "BSB : je suis la 2" ;
	pwd ;
	for v in $(filter-out $(MAKE_FILTERS),$(shell find .  -mindepth 1 -maxdepth 1 -type d -printf '%P\n')) ; do \
		if [ -f ${CURDIR}/$$v/Makefile ] ; then \
                	$(MAKE) --directory=$$v $@ only-native-arch=$(only-native-arch) arch-warning=$(arch-warning); \
		fi ; \
	done

# Output board name if arch match criteria or if there is no defined criteria (or filter)
list-boards:
	@if [ "$(board-arch)" = "" ] ; then \
			echo "$(BOARD_NAME)" ; \
	else \
			if [ "$(board-arch)" = "$(BOARD_ARCH)" ]; then \
				echo "$(BOARD_NAME)" ; \
			fi ; \
	fi ;

# Output board architecture. The ouput is sorted and deduplicated by caller
list-architectures:
	@echo "$(BOARD_ARCH)" ;

# Display the locally available versions
show-u-boot-dft-version:
#	find $$PWD/u-boot -mindepth 1 -maxdepth 1 -type d -printf '%P\n' | grep "\." | sort -r --sort=version | head -n 1
	@find ./u-boot -mindepth 1 -maxdepth 1 -type d -printf '%P\n' | grep "\." | sort -r --sort=version | head -n 1

show-kernel-dft-version:
	@find ./kernel -mindepth 1 -maxdepth 1 -type d -printf '%P\n' | grep "\." | sort -r --sort=version | head -n 1

show-u-boot-available-upgrade:
	@MY_ARCH=$(board-arch) ; \
	if [ "$(board-arch)" = "armhf" ] ; then \
		MY_ARCH="armv7l"; \
	fi ; \
	if [ "$(board-arch)" = "arm64" ] ; then \
		MY_ARCH="aarch64"; \
	fi ; \
	if [ "$(board-arch)" = "amd64" ] ; then \
		MY_ARCH="x86_64"; \
	fi ; \
	if [ "$(board-arch)" = "" ] || [ "$(BOARD_ARCH)" = "$$MY_ARCH" ] ; then \
		UBOOT_DFT_VERSION=$(shell find $$PWD/u-boot -mindepth 1 -maxdepth 1 -type d -printf '%P\n' | grep "\." | sort -r --sort=version | head -n 1) ; \
		UBOOT_UPSTREAM_VERSION=$(shell wget -O- https://github.com/u-boot/u-boot/releases 2>&1 | grep -v "rc" | grep "v20" | tr '<' ' ' | tr '>' ' ' | tr 'v' ' ' | head -n 2 | tail -n 1 | awk '{ print $$1 }') ; \
		if [ "$$UBOOT_DFT_VERSION" = "" ] ; then \
			echo "$(BOARD_NAME) has no u-boot version available, latest version ($$UBOOT_UPSTREAM_VERSION) can be added" ; \
		else \
			if [ ! "$$UBOOT_DFT_VERSION" = "$$UBOOT_UPSTREAM_VERSION" ] ; then \
				echo "$(BOARD_NAME) u-boot can be upgraded from $$UBOOT_DFT_VERSION to $$UBOOT_UPSTREAM_VERSION" ; \
			else \
			  echo "$(BOARD_NAME) u-boot is up to date" ; \
			fi ; \
		fi ; \
	fi ;

show-kernel-available-upgrade:
	@MY_ARCH=$(board-arch) ; \
	if [ "$(board-arch)" = "armhf" ] ; then \
		MY_ARCH="armv7l"; \
	fi ; \
	if [ "$(board-arch)" = "arm64" ] ; then \
		MY_ARCH="aarch64"; \
	fi ; \
	if [ "$(board-arch)" = "amd64" ] ; then \
		MY_ARCH="x86_64"; \
	fi ; \
	if [ "$(board-arch)" = "" ] || [ "$(BOARD_ARCH)" = "$$MY_ARCH" ] ; then \
		KERNEL_DFT_VERSION=$(shell find kernel -mindepth 1 -maxdepth 1 -type d -printf '%P\n' | grep "\." | sort -r --sort=version | head -n 1) ; \
		KERNEL_UPSTREAM_VERSION=$(shell wget -O-  https://www.kernel.org/ 2>&1| grep "<td><strong>" | tr '<' ' ' | tr '>' ' ' | awk '{ print $$3 }' | head -n 2 | tail -n 1) ; \
		if [ "$$KERNEL_DFT_VERSION" = "" ] ; then \
			echo "$(BOARD_NAME) has no kernel version available, latest version ($$KERNEL_UPSTREAM_VERSION) can be added" ; \
		else \
			if [ ! "$$KERNEL_DFT_VERSION" = "$$KERNEL_UPSTREAM_VERSION" ] ; then \
				echo "$(BOARD_NAME) kernel can be upgraded from $$KERNEL_DFT_VERSION to $$KERNEL_UPSTREAM_VERSION" ; \
			else \
			  echo "$(BOARD_NAME) kernel is up to date" ; \
			fi ; \
		fi ; \
	fi ;
