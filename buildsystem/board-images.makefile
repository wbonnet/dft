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
	@if [ ! -e "${CURDIR}/buildsystem" ] ; then \
		echo "buildsystem symlink ${CURDIR}/buildsystem is Missing. It should be a symlink to ../buildsystem" ; \
		echo "You can fix with the following shell commands :" ; \
		echo "ln -s ../buildsystem ${CURDIR}/buildsystem" ; \
		echo "git add ${CURDIR}//buildsystem" ; \
		$(call dft_error ,2005-0205) ; \
	fi ; 
	@if [ ! "$(shell readlink ./Makefile)" = "$(DFT_BUILDSYSTEM)/board-images.makefile" ] ; then \
		echo "The target of symlink Makefile should be $(DFT_BUILDSYSTEM)/board-images.makefile in directory ${CURDIR}" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f ${CURDIR}/Makefile" ; \
		echo "ln -s $(DFT_BUILDSYSTEM)/board-images.makefile ${CURDIR}/Makefile" ; \
		echo "git add ${CURDIR}/Makefile" ; \
		$(call dft_error ,2005-0809) ; \
	fi ; 
	for image in $(shell find . -mindepth 1 -maxdepth 1 -type d -printf '%P\n') ; do \
		echo "Checking $(BOARD_NAME) image $$image definition" ; \
		if [ ! -L "$$image/Makefile" ] ; then \
			echo "Makefile symlink in ${CURDIR}/$$image is missing. It should be a symlink to ../$(DFT_BUILDSYSTEM)/board-image.makefile" ; \
			echo "You can fix with the following shell commands :" ; \
			echo "ln -s ../$(DFT_BUILDSYSTEM)/board-image.makefile ${CURDIR}/$$image/Makefile" ; \
			echo "git add ${CURDIR}/$$image/Makefile" ; \
			echo "make sanity-check" ; \
			$(call dft_error ,2005-0810) ; \
		fi ; \
		s=`readlink $$image/Makefile` ; \
		if [ !  "$$s" = "../$(DFT_BUILDSYSTEM)/board-image.makefile" ] ; then \
			echo "Makefile symlink in $$image must link to ../$(DFT_BUILDSYSTEM)/board-image.makefile" ; \
			echo "The link currently targets to $$s" ; \
			echo "You can fix with the following shell commands :" ; \
			echo "git rm -f ${CURDIR}/$$image/Makefile || rm -f ${CURDIR}/$$image/Makefile" ; \
			echo "ln -s ../$(DFT_BUILDSYSTEM)/board-image.makefile ${CURDIR}/$$image/Makefile" ; \
			echo "git add ${CURDIR}/$$image/Makefile" ; \
			echo "make sanity-check" ; \
			$(call dft_error ,2015-0813) ; \
		fi ; \
	done ; \
	
# ------------------------------------------------------------------------------
#
# Target that prints the help
#
help:
	@echo "Available (and recursive) targets are :"
	@echo "   list-images             Display the list of images available for board $(BOARD_NAME)"
	@echo "                           The following filters can be used to display only matching images : "
	@echo "                           type=(rootfs or firmware)."
	@echo "   sanity-check            Check the availability of required items (files, symlinks, directories) in subdirs"
	@echo "                           This target only warns you and do not make any change to the tree content."
	@echo "   help                    Display this help"

