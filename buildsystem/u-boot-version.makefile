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

# Defines variables specific to u-boot version level
SW_NAME          := u-boot
PATH_WORDS       := $(subst /, ,$(abspath Makefile))
SW_VERSIONFIELD  := $(shell echo $(PATH_WORDS) |  awk '{ print NF-1 }')
SW_VERSION       := $(shell echo $(PATH_WORDS) |  cut -d ' ' -f$(SW_VERSIONFIELD))

# Build system sould be available under board folder as a symlink. Keep it
# locally available under board folder computing a relative path is a nightmare
# and does not work in all cases. Environment variables are not git friendly
# since git add will loose variable name and generate an absolute path, which
# is not comptible with user need ans or workspace relocation nor packagng needs.
# better solutions wille be really welcomeds contributions.
# Include DFT build system shared Makfile includes
DFT_BUILDSYSTEM := buildsystem
include ../board.mk
include $(DFT_BUILDSYSTEM)/inc/u-boot.mk
include $(DFT_BUILDSYSTEM)/dft.mk

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

# u-boot version generic Makefile
#
# WARNING if you need to make any version specific modification or definition,
# Please take in consideration that you must not modify the content of this file.
# Otherwise it would modify the symlink target and become the new default value
# for all unmodified makefiles of all existing boards.

# Defines patches to apply to the upstream sources :
# PATCHFILES += 0000_some_patch.diff

# If you use the patch feature, please make a copy of this file to store
# the definition of the PATCHFILES variable. The previous line in comment is
# provided as an example of how to do it. Please duplicate, modify and
# uncomment the line. Files will be searched for in the files/ directory at
# the same level as this Makefile.

# Do not recurse the following subdirs
MAKE_FILTERS  = debian files patches

# ------------------------------------------------------------------------------
#
# Targets not associated with a file (aka PHONY)
#


# ------------------------------------------------------------------------------
#
# Check folder content sanity (are all mandatory files and symlink available)
#
sanity-check:
	@echo "Checking $(BOARD_NAME) u-boot $(SW_VERSION) package definition" ; \
	if [ ! -f "../board.mk" ] ; then \
		echo "file board.mk is missing in directory ${CURDIR}/.." ; \
		$(call dft_error ,1911-1512) ; \
	fi ; \
	if [ ! -d "${CURDIR}/files" ] ; then \
		echo "files directory is missing in ${CURDIR}. It should contains a link to the markdown file install.$(SW_NAME)-$(BOARD_NAME).md needed by target package." ; \
		echo "You can fix this with the following commands : " ; \
		mkdir -p ${CURDIR}/files ; \
		touch ${CURDIR}/files/.gitkeep ; \
		ln -s ../files/install.$(SW_NAME)-$(BOARD_NAME).md ${CURDIR}/files/ ; \
		git add ${CURDIR}/files ; \
		$(call dft_error ,2004-2706) ; \
	fi ; \
	if [ ! -L "files/install.$(SW_NAME)-$(BOARD_NAME).md" ] ; then \
		echo "The link to the markdown file install.$(SW_NAME)-$(BOARD_NAME).md is missing in the ${CURDIR}/files directory." ; \
		echo "You can fix this with the following commands : " ; \
		mkdir -p ${CURDIR}/files ; \
		touch ${CURDIR}/files/.gitkeep ; \
		ln -s ../../files/install.$(SW_NAME)-$(BOARD_NAME).md ${CURDIR}/files/ ; \
		echo git add ${CURDIR}/files ; \
		$(call dft_error ,2004-2705) ; \
	fi ; \
	s=`readlink files/install.$(SW_NAME)-$(BOARD_NAME).md` ; \
	if [ ! "$$s" == "../../files/install.$(SW_NAME)-$(BOARD_NAME).md" ] ; then \
		echo "The link to the markdown file in ${CURDIR}/files must target to ../../files/install.$(SW_NAME)-$(BOARD_NAME).md" ; \
		echo "It currently tagets to $$s" ; \
		echo "You can fix this with the following shell commands :" ; \
		git rm -f files/install.$(SW_NAME)-$(BOARD_NAME).md || rm -f files/install.$(SW_NAME)-$(BOARD_NAME).md ; \
		ln -s ../../files/install.$(SW_NAME)-$(BOARD_NAME).md ${CURDIR}/files/ ; \
		git add ${CURDIR}/files ; \
		echo "la je merde sur le sur CURDIR et lechemin courant de la boucle for et make recursif" ; \
		$(call dft_warning ,2004-2705) ; \
	fi ; \
	if [ ! -d "${CURDIR}/patches" ] ; then \
		echo "patches directory is missing in ${CURDIR}. It is used to store patches to be applied on sources after extract and before build targets. By default it is an empty folder." ; \
		echo "You can fix this with the following commands : " ; \
		mkdir -p ${CURDIR}/patches ; \
		touch ${CURDIR}/patches/.gitkeep ; \
		git add ${CURDIR}/patches ; \
		$(call dft_error ,2004-2703) ; \
	fi ; \
	if [ ! -d "${CURDIR}/debian" ] ; then \
		echo "debian directory is missing in ${CURDIR}. It should contains the files needed to create the debian package for $(BOARD_NAME) u-boot." ; \
		$(call dft_error ,1911-1510) ; \
	fi ; \
	s=`readlink Makefile`; \
	if [ !  "$$s" == "$(DFT_BUILDSYSTEM)/u-boot-version.makefile" ] ; then \
		echo "Makefile symlink must link to $(DFT_BUILDSYSTEM)/u-boot-version.makefile" ; \
		echo "It currently tagets to $$s" ; \
		echo "You can fix this with the following shell commands :" ; \
		git rm -f Makefile || rm -f Makefile ; \
		ln -s $(DFT_BUILDSYSTEM)/u-boot-version.makefile Makefile ; \
		git add Makefile ; \
		$(call dft_error ,2004-2704) ; \
	fi ;

# ------------------------------------------------------------------------------
#
# Check defconfig target availability from upstream sources. It has to be done
# to detect target not supported by a given u-boot version. If defconfig is not
# available compilation nor package building will be successful. Version should
# be removed from git tree since upstream software doe not support this board.
#
check-u-boot-defconfig: extract
	@if [ "$(UBOOT_DEFCONFIG)" == "" ] ; then \
		echo "ERROR : Variable UBOOT_DEFCONFIG defining u-boot defconfig filename is not set or empty for board $(BOARD_NAME). Please set it in board.mk" ; \
		$(call dft_error ,2001-1002) ; \
	fi ;
	@echo "Checking $(UBOOT_DEFCONFIG) u-boot definition availability for version $(SW_VERSION)" ;
	if [ ! -f "$(BUILD_DIR)/configs/$(UBOOT_DEFCONFIG)" ] ; then \
		echo "ERROR : u-boot $(UBOOT_DEFCONFIG) defconfig is not available in version $(SW_VERSION). Make was working on board $(BOARD_NAME)" ; \
		$(call dft_error ,2001-1003) ; \
	fi ;

# Simple forwarder just  in case
u-boot-package : package
