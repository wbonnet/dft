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

# Do not recurse the following subdirs
MAKE_FILTERS  := Makefile workdir README.md .
SW_NAME       := SW_NAME_undefined_at_category_level

# Board category directory contains several folders, on per board in this category
# Each board folder must contain a board.mk file with board specific information,
# a mandatory kernel folder, optional folders like u-boot for boot loader and files
# to store needed additionnal files
sanity-check:
	@echo "DEBUG : in category.makefile target sanity-check" ;
	for board in $(shell find . -mindepth 1 -maxdepth 1 -type d ) ; do \
		echo "Now checking board $$board" ; \
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
			$(call dft_error ,2001-0202) ; \
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
	for folder in $(shell find . -mindepth 1 -maxdepth 1 -type d ) ; do \
		echo "DEBUG : Je vais tester le repertoire $$folder" ; \
		if [ -e $$folder/Makefile ] ; then \
			$(MAKE) --directory=$$folder sanity-check ; \
		else  \
			echo "Error there is no Makefile in ${CURDIR}/$$folder" ; \
			pwd ; \
			$(call dft_error ,2001-0205) ; \
		fi ; \
	done ;

# If package is called then make both u-boot and kernel-package
package: bsp-package
bsp: bsp-package
bsp-package: u-boot-package kernel-package

# Build only u-boot package target
do-configure:
	echo "DEBUG : configure in category.makefile" ;
	@for i in $(filter-out $(MAKE_FILTERS),$(shell find . -mindepth 1 -maxdepth 1 -type d )) ; do \
		if [ -f $$i/Makefile ] ; then \
			$(MAKE) --directory=$$i configure ; \
		fi ; \
        done

# Build only u-boot package target
u-boot-package:
	@echo "DEBUG : $@ in category.makefile" ;
	@for i in $(filter-out $(MAKE_FILTERS),$(shell find . -mindepth 1 -maxdepth 1 -type d )) ; do \
		if [ -f $$i/Makefile ] ; then \
			$(MAKE) --directory=$$i u-boot-package ; \
		fi ; \
        done

# Build only linux kernel an package target
linux-kernel-package:
kernel-package:
	@echo "DEBUG : $@ in category.makefile" ;
	@for i in $(filter-out $(MAKE_FILTERS),$(shell find . -mindepth 1 -maxdepth 1 -type d )) ; do \
		if [ -f $$i/Makefile ] ; then \
			$(MAKE) --directory=$$i kernel-package ; \
		fi ; \
        done

# Create a new u-boot version entry
add-u-boot-version:
	@echo "DEBUG : in category.makefile add-u-boot-version with argument new-version $(new-version)" ;
	@for i in $(filter-out $(MAKE_FILTERS),$(shell find . -mindepth 1 -maxdepth 1 -type d )) ; do \
		if [ -f $$i/Makefile ] ; then \
			$(MAKE) --warn-undefined-variables --print-directory --directory=$$i add-u-boot-version new-version=$(new-version) ; \
		fi ; \
        done

check-u-boot-defconfig:
	@for v in $(filter-out $(MAKE_FILTERS),$(shell find .  -mindepth 1 -maxdepth 1 -type d )) ; do \
		$(MAKE) --directory=$$v  check-u-boot-defconfig ; \
	done

# Create a new board entry
new-board:
	echo "DEBUG : in category.makefile running new-board with argument board_name $(board_name) board_arch $(board_arch) board_arch $(board_arch) uboot_support $(uboot_support) uboot_support $(uboot_support)  uboot_defconfig $(uboot_defconfig) default_dtb $(default_dtb)" ; \
	if [ "$(board_name)" == "" ] ; then \
		echo "DEBUG : from category.makefile argument board_name is missing or has no value. Doing nothing..." ; \
		$(call dft_error ,2001-1601) ; \
	fi ; \
	if [ "$(board_arch)" == "" ] ; then \
		echo "DEBUG : from category.makefile argument board_arch is missing or has no value. Doing nothing..." ; \
		$(call dft_error ,2001-1602) ; \
	fi ; \
	if [ -d "./$(board_name)" ] ; then \
		echo ". Board $(board_name) already exist. Doing nothing..." ; \
	else  \
		echo ". Creating the directory for board $(board_name)" ; \
		mkdir -p $(board_name) ; \
		cp  $(DFT_BUILDSYSTEM)/templates/board.mk.template $(board_name)/board.mk ; \
		sed -i -e "s/__BOARD_ARCH__/$(board_arch)/g" -e "s/__BOARD_NAME__/$(board_name)/g" $(board_name)/board.mk ; \
		ln -s buildsystem/board.makefile $(board_name)/Makefile ; \
		ln -s ../buildsystem $(board_name)/buildsystem ; \
	fi ; \
	if [ ! "$(uboot_defconfig)" == "" ] ; then \
		sed -i -e "s/__UBOOT_DEFCONFIG__/$(uboot_defconfig)/g" $(board_name)/board.mk ; \
	else  \
		sed -i -e "s/__UBOOT_DEFCONFIG__/$(uboot_defconfig)/g" $(board_name)/board.mk ; \
	fi ; \
	if [ ! "$(default_dtb)" == "" ] ; then \
		sed -i -e "s/__DEFAULT_DTB__/$(default_dtb)/g" $(board_name)/board.mk ; \
	else  \
		sed -i -e "s/__DEFAULT_DTB__/default.dtb/g" $(board_name)/board.mk ; \
	fi ; \
	if [ "$(uboot_support)" == "1" ] ; then \
		sed -i -e "s/__UBOOT_SUPPORT__/1/g" $(board_name)/board.mk ; \
	else  \
		if [ "$(uboot_support)" == "0" ] ; then \
			sed -i -e "s/__UBOOT_SUPPORT__/0/g" $(board_name)/board.mk ; \
		else  \
			echo "uboot_support value should be 0 or 1. No value is equivalent to 1, u-boot wiil be activated" ; \
		fi ; \
	fi ; \
	if [ "$(grub_support)" == "1" ] ; then \
		sed -i -e "s/__GRUB_SUPPORT__/1/g" $(board_name)/board.mk ; \
	else  \
		if [ "$(grub_support)" == "0" ] ; then \
			sed -i -e "s/__GRUB_SUPPORT__/0/g" $(board_name)/board.mk ; \
		else  \
			echo "grub_support value should be 0 or 1. No value is equivalent to 0, grub will be deactivated" ; \
			export grub-support=0 ; \
		fi ; \
	fi ; \
	if [ "$(uboot_defconfig)" == "" ] ; then \
		sed -i -e "s/__UBOOT_DEFCONFIG__/1/g" $(board_name)/board.mk ; \
	else  \
		if [ "$(grub_support)" == "0" ] ; then \
			sed -i -e "s/__GRUB_SUPPORT__/0/g" $(board_name)/board.mk ; \
		else  \
			echo "grub_support value should be 0 or 1. No value is equivalent to 0, grub will be deactivated" ; \
			export grub-support=0 ; \
		fi ; \
		mkdir $(board_name)/kernel/ ; \
		ln -s ../buildsystem $(board_name)/kernel/buildsystem ; \
		ln -s buildsystem/linux-kernel.makefile $(board_name)/kernel/Makefile ; \
		if [ "$(uboot_support)" == "1" ] ; then \
			mkdir $(board_name)/u-boot/ ; \
			ln -s ../buildsystem $(board_name)/u-boot/buildsystem ; \
			ln -s buildsystem/u-boot.makefile $(board_name)/u-boot/Makefile ; \
		fi ; \
		if [ "$(uboot_support)" == "1" ] ; then \
			echo "You work is still local, you now have to run : " ; \
			echo "git add $(board_name) then commit and push to make it available." ; \
			echo "then do a git commit and git push to make the new board entry available." ; \
			echo "The next step is to add at least a u-boot version to the newly created $(board_name) board. You can do it with following commands (change the version given as example) :" ; \
			echo "cd $(board_name)/u-boot" ; \
			echo "make new-version version=2020.10" ; \
		fi ; \
	fi ;

# Simple target forwarder
extract:
fetch:
setup:
	@for v in $(filter-out $(MAKE_FILTERS),$(shell find .  -mindepth 1 -maxdepth 1 -type d )) ; do \
		if [ -f ${CURDIR}/$$v/Makefile ] ; then \
                	$(MAKE) --directory=$$v $@ ; \
		fi ; \
	done

# ------------------------------------------------------------------------------
#
# Target that prints the help
#
help:
	@echo "The existing local targets are the following. Local targets are executed only at this"
	@echo "level in the category, without recursion nor walk down the tree of board categories"
