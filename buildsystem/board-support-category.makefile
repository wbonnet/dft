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
# Copyright 2019 DFT project (http://www.firmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#

# Build system sould be available under board folder as a symlink. Keep it
# locally available under board folder computing a relative path is a nightmare
# and does not work in all cases. Environment variables are not git friendly
# since git add will loose variable name and generate an absolute path, which
# is not comptible with user need ans or workspace relocation nor packagng needs.
# better solutions wille be really welcomeds contributions.
DFT_BUILDSYSTEM := buildsystem
include $(DFT_BUILDSYSTEM)/dft.mk

SW_NAME     ?= undefined-sw-name
SW_VERSION  ?= undefined-sw-version

# Do not recurse the following subdirs
MAKE_FILTERS  := Makefile workdir README.md .


# Board category directory contains several folders, one per board in the category
# Each board folder must contain a board.mk file with board specific information,
# a mandatory kernel folder, optional folders like 'u-boot' or 'grub' for
# boot loaders and 'files' to store needed additionnal files
sanity-check:
	@for board in $(shell find . -mindepth 1 -maxdepth 1 -type d -printf '%P\n') ; do \
		echo "Now checking manifest sanity for board $$board" ; \
		if [ ! -e "$$board/buildsystem" ] ; then \
			echo "buildsystem symlink ${CURDIR}/$$board/buildsystem is Missing. It should be a symlink to  $(DFT_BUILDSYSTEM)" ; \
			echo "You can fix with the following shell commands :" ; \
			ln -s ../$(DFT_BUILDSYSTEM) ${CURDIR}/$$board ; \
			git add ${CURDIR}/$$board/buildsystem ; \
			$(call dft_error ,2001-0201) ; \
		fi ; \
		if [ ! -e "$$board/kernel/buildsystem" ] ; then \
			echo "buildsystem symlink ${CURDIR}/$$board/kernel is Missing. It should be a symlink to  ../$(DFT_BUILDSYSTEM)" ; \
			echo "You can fix with the following shell commands :" ; \
			ln -s ../$(DFT_BUILDSYSTEM) ${CURDIR}/$$board/kernel ; \
			git add ${CURDIR}/$$board/kernel/buildsystem ; \
			$(call dft_error ,2001-0206) ; \
		fi ; \
		if [ ! -e "$$board/u-boot/buildsystem" ] ; then \
			echo "buildsystem symlink ${CURDIR}/$$board/u-boot is Missing. It should be a symlink to  ../$(DFT_BUILDSYSTEM)" ; \
			echo "You can fix with the following shell commands :" ; \
			ln -s ../$(DFT_BUILDSYSTEM) ${CURDIR}/$$board/u-boot ; \
			git add ${CURDIR}/$$board/u-boot/buildsystem ; \
			$(call dft_error ,2001-0203) ; \
		fi ; \
		if [ ! -e "$$board/Makefile" ] ; then \
			echo "Makefile in ${CURDIR}/$$board is Missing. It should be a symlink to  $(DFT_BUILDSYSTEM)/board.makefile" ; \
			echo "You can fix with the following shell commands :" ; \
			git rm -f ${CURDIR}/$$board/Makefile ; \
			ln -s $(DFT_BUILDSYSTEM)/board.makefile ${CURDIR}/$$board/Makefile ; \
			git add ${CURDIR}/$$board/Makefile ; \
			$(call dft_error ,2001-1101) ; \
		fi ; \
		s=`readlink ${CURDIR}/$$board/Makefile` ; \
		if [ ! "$$s" = "$(DFT_BUILDSYSTEM)/board.makefile" ] ; then \
			echo "Makefile symlink in ${CURDIR}/$$board must link to $(DFT_BUILDSYSTEM)/board.makefile" ; \
			git rm -f ${CURDIR}/$$board/Makefile ; \
			ln -s $(DFT_BUILDSYSTEM)/board.makefile ${CURDIR}/$$board/Makefile ; \
			git add ${CURDIR}/$$board/Makefile ; \
			$(call dft_error ,2001-0208) ; \
		fi ; \
		if [ ! -f $$board/board.mk ] ; then \
			echo "Board description file board.mk is missing in directory ${CURDIR}//$$board" ; \
			echo "You can fix with the following shell commands :" ; \
			echo "git rm -f $$board/Makefile" ; \
			echo "cp  $(DFT_BUILDSYSTEM)/board.mk.template ${CURDIR}//$$board/board.mk" ; \
			echo "git add ${CURDIR}/$$board/board.mk" ; \
			echo "Warning !!! : Dont forget to edit this file and replace 'unkown' values with board specific values" ; \
			$(call dft_error ,1911-1701) ; \
		fi ; \
	done ; \
	for folder in $(shell find . -mindepth 1 -maxdepth 1 -type d -printf '%P\n') ; do \
		if [ -e $$folder/Makefile ] ; then \
			$(MAKE) --no-print-directory sanity-check --directory=$$folder  ; \
		else  \
			echo "Error there is no Makefile in ${CURDIR}/$$folder" ; \
			pwd ; \
			$(call dft_error ,2001-0205) ; \
		fi ; \
	done ;

# If package is called then make both u-boot and kernel-package
bsp: bsp-package
bsp-package: u-boot-package kernel-package

# Build only u-boot package target
u-boot-package:
	@echo "DEBUG : $@ in category.makefile" ;
	@for i in $(filter-out $(MAKE_FILTERS),$(shell find . -mindepth 1 -maxdepth 1 -type d -printf '%P\n')) ; do \
		if [ -f $$i/Makefile ] ; then \
			$(MAKE) --no-print-directory u-boot-package --directory=$$i ; \
		fi ; \
        done

# Build only linux kernel an package target
linux-kernel-package:
kernel-package:
	@echo "DEBUG : $@ in category.makefile" ;
	@for i in $(filter-out $(MAKE_FILTERS),$(shell find . -mindepth 1 -maxdepth 1 -type d -printf '%P\n')) ; do \
		if [ -f $$i/Makefile ] ; then \
			$(MAKE) --no-print-directory kernel-package --directory=$$i  ; \
		fi ; \
        done

# Create a new u-boot version entry
add-u-boot-version:
	@echo "DEBUG : in category.makefile add-u-boot-version with argument add-version $(new-version)" ;
	@for i in $(filter-out $(MAKE_FILTERS),$(shell find . -mindepth 1 -maxdepth 1 -type d -printf '%P\n')) ; do \
		if [ -f $$i/Makefile ] ; then \
			$(MAKE) add-u-boot-version --warn-undefined-variables --no-print-directory --directory=$$i new-version=$(new-version) ; \
		fi ; \
        done

check-u-boot-defconfig:
	@for v in $(filter-out $(MAKE_FILTERS),$(shell find .  -mindepth 1 -maxdepth 1 -type d -printf '%P\n')) ; do \
		$(MAKE) --no-print-directory check-u-boot-defconfig --directory=$$v  ; \
	done

# Simple target forwarder
show-u-boot-available-upgrade:
	@for v in $(filter-out $(MAKE_FILTERS),$(shell find .  -mindepth 1 -maxdepth 1 -type d -printf '%P\n')) ; do \
		if [ -f ${CURDIR}/$$v/Makefile ] ; then \
                	$(MAKE) --no-print-directory --directory=$$v $@  only-native-arch=$(only-native-arch) arch-warning=$(arch-warning) arch=$(arch); \
		fi ; \
	done

show-kernel-available-upgrade:
	@for v in $(filter-out $(MAKE_FILTERS),$(shell find .  -mindepth 1 -maxdepth 1 -type d -printf '%P\n')) ; do \
		if [ -f ${CURDIR}/$$v/Makefile ] ; then \
                	$(MAKE) --no-print-directory --directory=$$v $@  only-native-arch=$(only-native-arch) arch-warning=$(arch-warning) arch=$(arch); \
		fi ; \
	done

extract:
	@for v in $(filter-out $(MAKE_FILTERS),$(shell find .  -mindepth 1 -maxdepth 1 -type d -printf '%P\n')) ; do \
		if [ -f ${CURDIR}/$$v/Makefile ] ; then \
                	$(MAKE) --no-print-directory --directory=$$v $@  only-native-arch=$(only-native-arch) arch-warning=$(arch-warning) arch=$(arch); \
		fi ; \
	done

fetch:
	@for v in $(filter-out $(MAKE_FILTERS),$(shell find .  -mindepth 1 -maxdepth 1 -type d -printf '%P\n')) ; do \
		if [ -f ${CURDIR}/$$v/Makefile ] ; then \
                	$(MAKE) --no-print-directory --directory=$$v $@  only-native-arch=$(only-native-arch) arch-warning=$(arch-warning) arch=$(arch); \
		fi ; \
	done

# Forward target call to subfolders where are stored the board.mk files specifying board architecture
list-architectures:
	@for board in $(filter-out $(MAKE_FILTERS),$(shell find .  -mindepth 1 -maxdepth 1 -type d -printf '%P\n')) ; do \
			$(MAKE) --no-print-directory --directory=$$board $@ ; \
	done | sort -u ;

list-boards:
	@MY_ARCH=$(arch) ; \
	if [ "$(arch)" = "armhf" ] ; then \
		MY_ARCH="armv7l"; \
	fi ; \
	if [ "$(arch)" = "arm64" ] ; then \
		MY_ARCH="aarch64"; \
	fi ; \
	if [ "$(arch)" = "amd64" ] ; then \
		MY_ARCH="x86_64"; \
	fi ; \
	for board in $(filter-out $(MAKE_FILTERS),$(shell find .  -mindepth 1 -maxdepth 1 -type d -printf '%P\n')) ; do \
		if [ ! "$sMY_AARCH" = "" ] ; then \
			$(MAKE) --no-print-directory --directory=$$board $@ arch=$$MY_ARCH; \
		else \
			$(MAKE) --no-print-directory --directory=$$board $@ ; \
		fi ; \
	done | sort -u ;

# Create a new board entry
add-board:
	@echo "DEBUG : in board-support-category.makefile running add-board with argument(s) board-name $(board-name) arch $(arch) arch $(arch) uboot-support $(uboot-support) grub-support $(grub-support) uboot-defconfig $(uboot-defconfig) default-dtb $(default-dtb)" ; \
	if [ "$(board-name)" == "" ] ; then \
		echo "DEBUG : from category.makefile argument board-name is missing or has no value. Doing nothing..." ; \
		$(call dft_error ,2009-2201) ; \
	fi ; \
	if [ "$(arch)" == "" ] ; then \
		echo "DEBUG : from category.makefile argument arch is missing or has no value. Doing nothing..." ; \
		$(call dft_error ,2009-2203) ; \
	fi ; \
	if [ "$(uboot-support)" == "" ] ; then \
		echo "DEBUG : from category.makefile argument uboot-support is missing or has no value. Doing nothing..." ; \
		$(call dft_error ,2010-0101) ; \
	fi ; \
	if [ "$(uboot-defconfig)" == "" ] ; then \
		echo "DEBUG : from category.makefile argument uboot-defconfig is missing or has no value. Doing nothing..." ; \
		$(call dft_error ,2010-0102) ; \
	fi ; \
	if [ "$(default-dtb)" == "" ] ; then \
		echo "DEBUG : from category.makefile argument defaul-dtb is missing or has no value. Doing nothing..." ; \
		$(call dft_error ,2010-0103) ; \
	fi ; \
	if [ -d "./$(board-name)" ] ; then \
		echo ". Board $(board-name) already exist. Doing nothing..." ; \
	else  \
		echo ". Creating the directory for board $(board-name)" ; \
		mkdir -p $(board-name) ; \
		cp  $(DFT_BUILDSYSTEM)/templates/board.mk.template $(board-name)/board.mk ; \
		cp  $(DFT_BUILDSYSTEM)/templates/board-blueprint.yml.template $(board-name)/blueprint-$(board-name).yml ; \
		sed -i -e "s/__BOARD_ARCH__/$(arch)/g" -e "s/__BOARD_NAME__/$(board-name)/g" $(board-name)/blueprint-$(board-name).yml ; \
		sed -i -e "s/__BOARD_ARCH__/$(arch)/g" -e "s/__BOARD_NAME__/$(board-name)/g" $(board-name)/board.mk ; \
		if [ ! "$(uboot-defconfig)" == "" ] ; then \
			sed -i -e "s/__UBOOT_DEFCONFIG__/$(uboot-defconfig)/g" $(board-name)/board.mk ; \
		else  \
			sed -i -e "s/__UBOOT_DEFCONFIG__/unknown_defconfig/g" $(board-name)/board.mk ; \
			echo "uboot-defconfig variable was not set on make commande line, you will have to set it manually in $(board-name)/board.mk It is currely defined to unknown_defconffig by defaul and thus won't compile" ; \
		fi ; \
		if [ ! "$(default-dtb)" == "" ] ; then \
			sed -i -e "s/__DEFAULT_DTB__/$(default-dtb)/g" $(board-name)/board.mk ; \
		else  \
			sed -i -e "s/__DEFAULT_DTB__/default.dtb/g" $(board-name)/board.mk ; \
		fi ; \
		if [ "$(uboot-support)" == "1" ] ; then \
			sed -i -e "s/__UBOOT_SUPPORT__/1/g" $(board-name)/board.mk ; \
		else  \
			if [ "$(uboot-support)" == "0" ] ; then \
				sed -i -e "s/__UBOOT_SUPPORT__/0/g" $(board-name)/board.mk ; \
			else  \
				echo "uboot-support value should be 0 or 1. No value is equivalent to 1, thus u-boot is activated" ; \
			fi ; \
		fi ; \
		if [ "$(grub-support)" == "1" ] ; then \
			sed -i -e "s/__GRUB_SUPPORT__/1/g" $(board-name)/board.mk ; \
		else  \
			if [ "$(grub-support)" == "0" ] ; then \
				sed -i -e "s/__GRUB_SUPPORT__/0/g" $(board-name)/board.mk ; \
			else  \
				echo "grub-support value should be 0 or 1. No value is equivalent to 0, thus grub is deactivated" ; \
				export grub-support=0 ; \
			fi ; \
		fi ; \
		ln -s buildsystem/board-support-board.makefile $(board-name)/Makefile ; \
		ln -s ../buildsystem $(board-name)/buildsystem ; \
	fi ; \
	mkdir $(board-name)/kernel ; \
	mkdir $(board-name)/kernel/config ; \
	touch $(board-name)/kernel/config/.gitkeep ; \
	ln -s ../board.mk $(board-name)/kernel/ ; \
	ln -s ../buildsystem $(board-name)/kernel/ ; \
	ln -s buildsystem/linux-kernel.makefile $(board-name)/kernel/Makefile ; \
	if [ "$(uboot-support)" == "1" ] ; then \
		mkdir $(board-name)/u-boot/ ; \
		mkdir $(board-name)/u-boot/files/ ; \
		touch $(board-name)/u-boot/files/.gitkeep ; \
		ln -s ../buildsystem $(board-name)/u-boot/ ; \
		ln -s ../board.mk $(board-name)/u-boot/ ; \
		cp  $(DFT_BUILDSYSTEM)/templates/u-boot.install.template $(board-name)/u-boot/files/install.u-boot-$(board-name).md ; \
		sed -i -e "s/__BOARD_NAME__/$(board-name)/g" $(board-name)/u-boot/files/install.u-boot-$(board-name).md ; \
		ln -s buildsystem/u-boot.makefile $(board-name)/u-boot/Makefile ; \
		echo "Your work is still local, to make it available, you have to run git add commit and push : " ; \
		echo "git add $(board-name)" ; \
		echo "Last step before building is to add a u-boot version to the new $(board-name) board. You can use this example :" ; \
		echo "cd $(board-name)/u-boot" ; \
		echo "make add-u-boot-version new-version=2020.04" ; \
	fi ;
	echo "The next steps are to add u-boot and kernel versions definition to $(board-name) board. You can use this example :" ; \
	echo "cd $(board-name) && make add-u-boot-version new-version=YYYY.MM" ; \
	echo "cd kernel && make add-linux-kernel-version new-version=AA.BB.CC && cd ../.." ; \
	echo ; \
	echo "Your work is still local, to make it available, you have to run git add commit and push : " ; \
	echo "git add $(board-name)" ; \

# ------------------------------------------------------------------------------
#
# Target that prints the help
#
help:
	@echo "Available targets are :"
	@echo "   list-architectures      Display the list of supported board in this category"
	@echo "   list-boards             Display the list of supported architectures in this category"
	@echo "   help                    Display this help"
