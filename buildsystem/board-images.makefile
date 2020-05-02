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

# Force bash use instead of sh which is a symlink to dash on Debian. Dash use
# a slightly different syntax for some operators. This way it a known shell.
SHELL := bash

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

# List available images
list-images:
	@for v in $(filter-out $(MAKE_FILTERS),$(shell find .  -mindepth 1 -maxdepth 1 -type d -printf '%P\n')) ; do \
		if [ -f ${CURDIR}/$$v/Makefile ] ; then \
                	$(MAKE) --directory=$$v list-images ; \
		fi ; \
	done

sanity-check:
	@if [ ! -e "${CURDIR}/$$v/buildsystem" ] ; then \
		echo "buildsystem symlink ${CURDIR}/$$v/buildsystem is Missing. It should be a symlink to ../buildsystem" ; \
		echo "You can fix with the following shell commands :" ; \
		echo "ln -s ../buildsystem ${CURDIR}/$$v/buildsystem" ; \
		echo "git add ${CURDIR}/$$v/buildsystem" ; \
		$(call dft_error ,2005-0205) ; \
	fi ; \
	if [ "$(UBOOT_SUPPORT)" == "1"  ] ; then \
		echo "Checking $(BOARD_NAME) u-boot packages folder" ; \
		if [ ! -L "Makefile"  ] ; then \
			echo "Makefile symlink $(DFT_BUILDSYSTEM)/u-boot.makefile is missing in directory ${CURDIR}" ; \
			echo "You can fix with the following commands : " ; \
			echo "git rm -f ${CURDIR}/Makefile" ; \
			echo "ln -s $(DFT_BUILDSYSTEM)/u-boot.makefile ${CURDIR}/Makefile" ; \
			echo "git add ${CURDIR}/Makefile" ; \
			$(call dft_error ,2001-0810) ; \
		fi ; \
		if [ ! "$(shell readlink ./Makefile)" = "$(DFT_BUILDSYSTEM)/$(SW_NAME).makefile" ] ; then \
			echo "The target of symlink Makefile should be $(DFT_BUILDSYSTEM)/$(SW_NAME).makefile in directory ${CURDIR}" ; \
			echo "You can fix with the following commands : " ; \
			echo "git rm -f ${CURDIR}/Makefile" ; \
			echo "ln -s $(DFT_BUILDSYSTEM)/u-boot.makefile ${CURDIR}/Makefile" ; \
			echo "git add ${CURDIR}/Makefile" ; \
			$(call dft_error ,2001-0809) ; \
		fi ; \
		if [ ! -d "${CURDIR}/files" ] ; then \
			echo "The files directory is missing in ${CURDIR}. It should contains the markdown file install.u-boot-$(BOARD_NAME).md needed by target package." ; \
			echo "You can fix with the following commands : " ; \
			echo "mkdir -p ${CURDIR}/files" ; \
			echo "touch ${CURDIR}/files/.gitkeep" ; \
			echo "ln -s ../../files/install.$(SW_NAME)-$(BOARD_NAME).md ${CURDIR}/files/" ; \
			echo "git add ${CURDIR}/files" ; \
			$(call dft_error ,2001-0808) ; \
		fi ; \
		if [ ! -f "${CURDIR}/files/install.$(SW_NAME)-$(BOARD_NAME).md" ] ; then \
			ls -lh "${CURDIR}/files/install.$(SW_NAME)-$(BOARD_NAME).md" ;  \
			echo "the $(SW_NAME) installation procedure is missing in the files/ folder. This folder should contain a file named install.$(SW_NAME)-$(BOARD_NAME).md describing. This file is needed by target package." ; \
			$(call dft_error ,2001-0806) ; \
		fi ; \
		if [ ! -L "board.mk" ] ; then \
			echo "The board.mk symlink to ../board.mk is missing in directory ${CURDIR}" ; \
			echo "You can fix with the following commands : " ; \
			echo "ln -s ../board.mk board.mk" ; \
			echo "git add board.mk" ; \
			$(call dft_error ,2001-0805) ; \
		fi ; \
		if [ ! "$(shell readlink ${CURDIR}/board.mk)" = "../board.mk" ] ; then \
			echo "The target of symlink board.mk should be ../board.mk in directory ${CURDIR}" ; \
			echo "You can fix with the following commands : " ; \
			echo "git rm -f ${CURDIR}/board.mk" ; \
			echo "ln -s ../board.mk ${CURDIR}/board.mk" ; \
			echo "git add ${CURDIR}/board.mk" ; \
			echo "make sanity-check" ; \
			$(call dft_error ,2001-0804) ; \
		fi ; \
		for version in $(shell find . -mindepth 1 -maxdepth 1 -type d -name '*\.*' ) ; do \
			echo "Checking $(BOARD_NAME) u-boot $$version package definition" ; \
			if [ ! -L "$$version/Makefile" ] ; then \
				echo "version folder $$version" ; \
				echo "Makefile symlink in ${CURDIR}/$$version is missing. It should be a symlink to $(DFT_BUILDSYSTEM)/$(SW_NAME)-version.makefile" ; \
				echo "You can fix with the following shell commands :" ; \
				if [ -f "$$version/Makefile" ] ; then \
					echo "git rm ${CURDIR}//$$version/Makefile" ; \
				fi ; \
				echo "ln -s ../../$(DFT_BUILDSYSTEM)/$(SW_NAME)-version.makefile ${CURDIR}/$$version/Makefile" ; \
				echo "git add ${CURDIR}//$$version/Makefile" ; \
				echo "make sanity-check" ; \
				$(call dft_error ,1911-2118) ; \
			fi ; \
			s=`readlink $$version/Makefile` ; \
			if [ !  "$$s" = "buildsystem/$(SW_NAME)-version.makefile" ] ; then \
				echo "Makefile symlink in $$version must link to buildsystem/$(SW_NAME)-version.makefile" ; \
				echo "The link currently targets to $$s" ; \
				echo "You can fix with the following shell commands :" ; \
				echo "git rm -f ${CURDIR}/$$version/Makefile || rm -f ${CURDIR}/$$version/Makefile" ; \
				echo "ln -s buildsystem/$(SW_NAME)-version.makefile ${CURDIR}/$$version/Makefile" ; \
				echo "git add ${CURDIR}//$$version/Makefile" ; \
				echo "make sanity-check" ; \
				$(call dft_error ,2015-0803) ; \
			fi ; \
		done ; \
	fi ; \
	
# ------------------------------------------------------------------------------
#
# Target that prints the help
#
help:
	@echo "Available targets are :"
	@echo "   list-images             Display the list of images available for board $(BOARD_NAME)"
	@echo "                           The following filters can be used to display only matching images : "
	@echo "                           type=(rootfs or firmware)."
	@echo "   sanity-check            Check the availability of required items (files, symlinks, directories) in subdirs"
	@echo "                           This target only warns you and do not make any change to the tree content."
	@echo "   help                    Display this help"
	@echo ""
	@echo "The existing local targets are the following. Local targets are executed only at this"
	@echo "level in the category, without recursion nor walk down the tree of board categories"
	@echo "   help                    Display this help"

