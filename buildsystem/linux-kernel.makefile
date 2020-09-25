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
#		William Bonnet	 	wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#

# Defines variables specific to Linux kernel
SW_NAME	   := linux

# Build system sould be available under board folder as a symlink. Keep it
# locally available under board folder computing a relative path is a nightmare
# and does not work in all cases. Environment variables are not git friendly
# since git add will loose variable name and generate an absolute path, which
# is not comptible with user need ans or workspace relocation nor packagng needs.
# better solutions wille be really welcomeds contributions.

DFT_BUILDSYSTEM := buildsystem
include ../board.mk
include $(DFT_BUILDSYSTEM)/inc/linux-kernel.mk
include $(DFT_BUILDSYSTEM)/dft.mk

# Strip the variables defined in board.mk to remove trailing whitespaces or
# some calls will fail (when passing defconfig name etc.)
BOARD_NAME      := $(subst ,,$(BOARD_NAME))
BOARD_ARCH      := $(subst ,,$(BOARD_ARCH))
UBOOT_SUPPORT   := $(subst ,,$(UBOOT_SUPPORT))
UBOOT_DEFCONFIG := $(subst ,,$(UBOOT_DEFCONFIG))
USE_CONFIG_FILE := $(subst ,,$(USE_CONFIG_FILE))

# Do not recurse the following subdirs
MAKE_FILTERS  := files config Makefile README.md .

# ------------------------------------------------------------------------------
#
# Mandatory defines that have to be defined at least in the main Makefile
#
ifeq ($(SW_NAME),)
$(error SW_NAME is not set)
endif

ifeq ($(DOWNLOAD_TOOL),)
$(error DOWNLOAD_TOOL is not set)
endif

# ------------------------------------------------------------------------------
#
# Targets not associated with a file (aka PHONY)
#

#
# Board level directory generic Linux kernel makefile
#

sanity-check:
	@echo "Checking $(BOARD_NAME) kernel packages folder"
	@if [ ! -d "${CURDIR}/config" ] ; then \
		echo "The directory config is missing in ${CURDIR}. It contains the configuration files of the different Linux kernel versions." ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir -p ${CURDIR}/config" ; \
		echo "touch ${CURDIR}/config/.gitkeep" ; \
		echo "git add ${CURDIR}/config/.gitkeep" ; \
		echo "make sanity-check" ; \
		$(call dft_error ,2001-0809) ; \
	fi ;
	@if [ ! -L "Makefile"  ] ; then \
		echo "The Makefile symlink to $(DFT_BUILDSYSTEM)/$(SW_NAME)-kernel.makefile is missing in directory ${CURDIR}" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f ${CURDIR}/Makefile" ; \
		echo "ln -s $(DFT_BUILDSYSTEM)/$(SW_NAME)-kernel.makefile ${CURDIR}/Makefile" ; \
		echo "git add ${CURDIR}/Makefile" ; \
		echo "make sanity-check" ; \
		$(call dft_error ,1911-2110) ; \
	fi ;
	@if [ ! "$(shell readlink ./Makefile)" = "$(DFT_BUILDSYSTEM)/$(SW_NAME)-kernel.makefile" ] ; then \
		echo "The target of symlink Makefile should be $(DFT_BUILDSYSTEM)/$(SW_NAME)-kernel.makefile in directory ${CURDIR}" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f ${CURDIR}/Makefile" ; \
		echo "ln -s $(DFT_BUILDSYSTEM)/$(SW_NAME)-kernel.makefile ${CURDIR}/Makefile" ; \
		echo "git add ${CURDIR}/Makefile" ; \
		echo "make sanity-check" ; \
		$(call dft_error ,1911-2011) ; \
	fi ;
	@if [ ! -d "${CURDIR}/config" ] ; then \
		echo "The directory config is missing in ${CURDIR}/. It contains the configuration files of the different Linux kernel versions." ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir -p ${CURDIR}/config" ; \
		echo "touch ${CURDIR}/config/.gitkeep" ; \
		echo "git add ${CURDIR}/config/.gitkeep" ; \
		echo "make sanity-check" ; \
		$(call dft_error ,1911-2013) ; \
	fi ;
	@if [ ! -L "board.mk" ] ; then \
		echo "The board.mk symlink to ../board.mk is missing in directory ${CURDIR}/" ; \
		echo "You can fix with the following commands : " ; \
		echo "ln -s ../board.mk ${CURDIR}/board.mk" ; \
		echo "git add ${CURDIR}/board.mk" ; \
		echo "make sanity-check" ; \
		$(call dft_error ,1911-1604) ; \
	fi ;
	@if [ ! "$(shell readlink board.mk)" = "../board.mk" ] ; then \
		echo "The target of symlink board.mk should be ../board.mk in directory ${CURDIR}/" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f ${CURDIR}/board.mk" ; \
		echo "ln -s ../board.mk ${CURDIR}/board.mk" ; \
		echo "git add ${CURDIR}/board.mk" ; \
		echo "make sanity-check" ; \
		$(call dft_error ,1911-1605) ; \
	fi ;
	@for version in $(filter-out $(MAKE_FILTERS),$(shell find . -mindepth 1 -maxdepth 1 -name "2*" -type d -printf '%P\n' )) ; do \
		echo "Checking $(BOARD_NAME) kernel $$version package definition" ; \
		if [ ! -L "$$version/Makefile" ] ; then \
			echo "version folder $$version" ; \
			echo "Makefile symlink in ${CURDIR}/$$version is missing. It should be a symlink to $(DFT_BUILDSYSTEM)/$(SW_NAME)-kernel-version.makefile" ; \
			echo "You can fix with the following shell commands :" ; \
			if [ -f "$$version/Makefile" ] ; then \
				echo "git rm ${CURDIR}/$$version/Makefile" ; \
			fi ; \
			echo "ln -s ../../$(DFT_BUILDSYSTEM)/$(SW_NAME)-kernel-version.makefile ${CURDIR}/$$version/Makefile" ; \
			echo "git add ${CURDIR}/$$version/Makefile" ; \
			echo "make sanity-check" ; \
			$(call dft_error ,1911-1607) ; \
		fi ; \
		if [ ! -e "config/$(BOARD_NAME)-kernel-$$version.config" ] ; then \
			echo "Kernel configuration file $(BOARD_NAME)-kernel-$$version.config is missing" ; \
			$(call dft_warning ,2004-2710) ; \
		fi ; \
		s=`readlink $$version/Makefile` ; \
		if [ !  "$$s" = "buildsystem/$(SW_NAME)-kernel-version.makefile" ] ; then \
			echo "Makefile symlink in $$version must link to buildsystem/$(SW_NAME)-kernel-version.makefile" ; \
			echo "it currently targets to $$s" ; \
			echo "You can fix with the following shell commands :" ; \
			echo "git rm -f ${CURDIR}/$$version/Makefile || rm -f ${CURDIR}/$$version/Makefile" ; \
			echo "ln -s buildsystem/$(SW_NAME)-kernel-version.makefile ${CURDIR}/$$version/Makefile" ; \
			echo "git add ${CURDIR}/$$version/Makefile" ; \
			echo "make sanity-check" ; \
			$(call dft_error ,1911-2118) ; \
		fi ; \
	done ;
	@for version in $(filter-out $(MAKE_FILTERS),$(shell find . -mindepth 1 -maxdepth 1 -name "*\.*" -type d -printf '%P\n' )) ; do \
		if [ -f $$version/Makefile ] ; then \
			$(MAKE) --no-print-directory --directory=$$version sanity-check || $(call dft_error ,2004-2708); \
		fi ; \
	done ;

# Create a new linux-kernel version entry
add-linux-kernel-version:
	@if [ "$(new-version)" == "" ] ; then \
		echo "WARNING : from linux-kernel.makefile argument new-version is missing or has no value. Doing nothing..." ; \
		$(call dft_error ,2001-0801) ; \
	fi ;
	@if [ -d "./$(new-version)" ] ; then \
		echo ". Version $(new-version) already exist. Doing nothing..." ; \
	else  \
		echo ". Creating the directory for linux-kernel version $(new-version)" ; \
		mkdir -p $(new-version) ; \
		ln -s ../$(DFT_BUILDSYSTEM) $(new-version)/buildsystem ; \
		ln -s ../$(DFT_BUILDSYSTEM)/linux-kernel-version.makefile $(new-version)/Makefile ; \
		mkdir -p $(new-version)/patches ; \
		touch $(new-version)/patches/.gitkeep ; \
		cp -fr ../$(DFT_BUILDSYSTEM)/templates/debian-linux-kernel-package $(new-version)/debian ; \
		mv $(new-version)/debian/linux-headers.install $(new-version)/debian/linux-headers-$(BOARD_NAME).install ; \
		for suffix in install postinst postrm preinst prerm ; do \
		mv $(new-version)/debian/linux-kernel.$(suffix) $(new-version)/debian/linux-kernel-$(BOARD_NAME).$(suffix) ; \



    mv $(new-version)/debian/linux-kernel.install $(new-version)/debian/linux-kernelheaders-$(BOARD_NAME).install ; \
    linux-kernel.postinst
    linux-kernel.postrm
    linux-kernel.preinst
    linux-kernel.prerm
		find $(new-version)/debian -type f | xargs sed -i -e "s/__SW_VERSION__/$(new-version)/g" \
                                           -e "s/__BOARD_NAME__/$(BOARD_NAME)/g" \
                                           -e "s/__DATE__/$(shell LC_ALL=C date +"%a, %d %b %Y %T %z")/g" ; \
		if [ "${DEBEMAIL}" = "" ] ; then \
			find $(new-version)/debian -type f | xargs sed -i -e "s/__MAINTAINER_EMAIL__/unknown/g" ; \
		else \
			find $(new-version)/debian -type f | xargs sed -i -e "s/__MAINTAINER_EMAIL__/${DEBEMAIL}/g" ; \
		fi ; \
		if [ "${DEBFULLNAME}" = "" ] ; then \
			find $(new-version)/debian -type f | xargs sed -i -e "s/__MAINTAINER_NAME__/unknown/g" ; \
		else \
			find $(new-version)/debian -type f | xargs sed -i -e "s/__MAINTAINER_NAME__/${DEBFULLNAME}/g" ; \
		fi ; \
		git add $(new-version) ; \
	fi ;

# Override standard targets
# upaload is overriden too otherwise make would walk through arch and latest tests and build because of dependancies
build configure package install upload :
	@if [ ! "x$(HOST_ARCH)" = "x$(BOARD_ARCH)" ] ; then \
		echo "Makefile processing had to be stopped during target $@ execution. The target board is based on $(BOARD_ARCH) architecture and make is running on a $(HOST_ARCH) board." ; \
	 	echo "Cross compilation is not supported. The generated binaries might be invalid or scripts could fail before reaching the end of target." ; \
		echo "Makefile will now continue and process only $(HOST_ARCH) based boards. You can get the missing binaries by running this target again on a $(BOARD_ARCH) based host and collect by yourself the generated items." ; \
		echo "To generate binaries for all architectures you need several builders, one for each target architecture flavor." ; \
	else \
		if [ "$(only-latest)" = "1" ] ; then \
			$(MAKE) --no-print-directory -C $(SW_LATEST) $@ only-native-arch=$(only-native-arch) arch-warning=$(arch-warning); \
		else \
			for v in $(filter-out $(MAKE_FILTERS),$(shell find .  -mindepth 1 -maxdepth 1 -type d  -name "2*" -printf '%P\n')) ; do \
				$(MAKE) --no-print-directory -C $$v $@ only-native-arch=$(only-native-arch) arch-warning=$(arch-warning); \
			done ; \
		fi ; \
	fi ; \
