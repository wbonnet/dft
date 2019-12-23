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
#	William Bonnet	 wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#

# Defines variables specific to Linux kernel
SW_NAME	= linux
SW_VERSION = no-version-at-kernel
buildsystem := ../../../../buildsystem
include board.mk
include $(buildsystem)/inc/linux-kernel.mk
include $(buildsystem)/dft.mk

# Do not recurse the following subdirs
MAKE_FILTERS  = files defconfig Makefile README.md .


# ------------------------------------------------------------------------------
#
# Mandatory defines that have to be defined at least in the main Makefile
#

ifndef SW_NAME
$(error SW_NAME is not set)
endif

ifndef DOWNLOAD_TOOL
$(error DOWNLOAD_TOOL is not set)
endif

# ------------------------------------------------------------------------------
#
# Targets not associated with a file (aka PHONY)
#
.PHONY: help clean mrproper

# 
# Board level birectory generic Linux kernel makefile
#

sanity-check:
	@echo "Checking $(BOARD_NAME) kernel packages folder" 
	@if [ ! -d "${CURDIR}/defconfig" ] ; then \
		echo "defconfig directory is missing in ${CURDIR}. It contains the configuration files of the different Linux kernel versions." ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir -p ${CURDIR}/defconfig" ; \
		echo "touch ${CURDIR}/defconfig/.gitkeep" ; \
		echo "git add ${CURDIR}//defconfig/.gitkeep" ; \
		false ; \
	fi ;
	@if [ ! -L "Makefile"  ] ; then \
		echo "Makefile symlink $(buildsystem)/$(SW_NAME)-kernel.makefile is missing in directory ${CURDIR}" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f ${CURDIR}//Makefile" ; \
		echo "ln -s $(buildsystem)/$(SW_NAME)-kernel.makefile ${CURDIR}//Makefile" ; \
		echo "git add ${CURDIR}//Makefile" ; \
		echo "error 191121-010" ; \
		exit 1 ; \
	fi ;
	@if [ ! "$(shell readlink ./Makefile)" = "$(buildsystem)/$(SW_NAME)-kernel.makefile" ] ; then \
		echo "target of symlink Makefile should be $(buildsystem)/$(SW_NAME)-kernel.makefile in directory ${CURDIR}/" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f ${CURDIR}//Makefile" ; \
		echo "ln -s $(buildsystem)/$(SW_NAME)-kernel.makefile ${CURDIR}/Makefile" ; \
		echo "git add ${CURDIR}/Makefile" ; \
		echo "error 1911120-011" ; \
		exit 1 ; \
	fi ;
	@if [ ! -d "${CURDIR}//defconfig" ] ; then \
		echo "defconfig directory is missing in ${CURDIR}/. It contains the configuration files of the different Linux kernel versions." ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir -p ${CURDIR}//defconfig" ; \
		echo "touch ${CURDIR}//defconfig/.gitkeep" ; \
		echo "git add ${CURDIR}//defconfig/.gitkeep" ; \
		echo "error 191120-013" ; \
 		exit 1 ; \
	fi ;
	@if [ ! -L "board.mk" ] ; then \
		echo "board.mk symlink to ../board.mk is missing in directory ${CURDIR}/" ; \
		echo "You can fix with the following commands : " ; \
		echo "ln -s ../board.mk ${CURDIR}//board.mk" ; \
		echo "git add ${CURDIR}//board.mk" ; \
		echo "error 1911116-04" ; \
		exit 1 ; \
	fi ;
	@if [ ! "$(shell readlink board.mk)" = "../board.mk" ] ; then \
		echo "target of symlink board.mk should be ../board.mk in directory ${CURDIR}/" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f ${CURDIR}/${CURDIR}/board.mk" ; \
		echo "ln -s ../board.mk ${CURDIR}/board.mk" ; \
		echo "git add ${CURDIR}/board.mk" ; \
		echo "error 1911116-05" ; \
		exit 1 ; \
	fi ;
	@for version in $(shell find . -mindepth 1 -maxdepth 1 -type d  -name '*\.*' ) ; do \
		echo "Checking $(BOARD_NAME) kernel $$version package definition" ; \
		if [ ! -L "$$version/Makefile" ] ; then \
			echo "version folder $$version" ; \
			echo "Makefile symlink in ${CURDIR}/$$version is missing. It should be a symlink to $(buildsystem)/$(SW_NAME)-kernel-version.makefile" ; \
			echo "You can fix with the following shell commands :" ; \
			if [ -f "$$version/Makefile" ] ; then \
				git rm ${CURDIR}//$$version/Makefile ; \
			fi ; \
			ln -s ../$(buildsystem)/$(SW_NAME)-kernel-version.makefile ${CURDIR}//$$version/Makefile ; \
			git add ${CURDIR}//$$version/Makefile ; \
			echo "exit 191116-07" ; \
		fi ; \
		s=`readlink $$version/Makefile` ; \
		if [ !  "$$s" = "../$(buildsystem)/$(SW_NAME)-kernel-version.makefile" ] ; then \
			echo "Makefile symlink in $$version must link to $(buildsystem)/$(SW_NAME)-kernel-version.makefile" ; \
			echo "You can fix with the following shell commands :" ; \
			git rm -f ${CURDIR}/$$version/Makefile || rm -f ${CURDIR}/$$version/Makefile ; \
			ln -s ../$(buildsystem)/$(SW_NAME)-kernel-version.makefile ${CURDIR}//$$version/Makefile ; \
			git add ${CURDIR}//$$version/Makefile ; \
			echo "exit 191122-20" ; \
		fi ; \
	done ; 
	@for folder in $(shell find . -mindepth 1 -maxdepth 1 -type d -name '*\.*') ; do \
		if [ -f $$folder/Makefile ] ; then \
			cd $$folder && $(MAKE) sanity-check && cd .. ; \
		fi ; \
	done ;

# Catch all target. Call the same targets in each subfolder
%:
	@for folder in $(filter-out $(MAKE_FILTERS),$(shell find . -mindepth 1 -maxdepth 1 -type d )) ; do \
		if [ -f $$folder/Makefile ] ; then \
			cd $$folder && $(MAKE) $* && cd .. ; \
		fi ; \
	done
