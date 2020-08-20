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
MAKE_FILTERS  := Makefile workdir README.md . buildsystem

# Forward sanity-check in subdirs
sanity-check:
	for board in $(filter-out $(MAKE_FILTERS),$(shell find .  -mindepth 1 -maxdepth 1 -type d -printf '%P\n')) ; do \
		if [ ! -L "${CURDIR}/$$board/buildsystem" ] ; then \
			echo "The buildsystem symlink in ${CURDIR}/$$board/ is Missing. It should be a symlink to ../buildsystem" ; \
			echo "You can fix with the following shell commands :" ; \
			echo "ln -s ../buildsystem ${CURDIR}/$$board/buildsystem" ; \
			echo "git add ${CURDIR}/$$board/buildsystem" ; \
			echo "make sanity-check" ; \
			$(call dft_error ,2005-0204) ; \
		fi ; \
		if [ ! -L "${CURDIR}/$$board/board.mk" ] ; then \
			echo "The board.mk symlink in ${CURDIR}/$$board is Missing. It should be a symlink to ../../board-support/$(shell basename `pwd`)/$$board/board.mk" ; \
			echo "You can fix with the following shell commands :" ; \
			echo "ln -s ../../board-support/$(shell basename `pwd`)/$$board/board.mk ${CURDIR}/$$board/board.mk" ; \
			echo "git add ${CURDIR}/$$board/board.mk" ; \
			echo "make sanity-check" ; \
			$(call dft_error ,2005-0304) ; \
		fi ; \
		if [ -f ${CURDIR}/$$v/Makefile ] ; then \
                	$(MAKE) --no-print-directory --directory=$$board sanity-check ; \
		fi ; \
	done

list-images:
	@echo "DEBUG list-images in board-images-category.makefile"
	@echo "DEBUG list-images is still TO TODO"
	@for v in $(filter-out $(MAKE_FILTERS),$(shell find .  -mindepth 1 -maxdepth 1 -type d -printf '%P\n')) ; do \
		if [ -f ${CURDIR}/$$v/Makefile ] ; then \
                	$(MAKE) --no-print-directory --directory=$$v list-images ; \
		fi ; \
	done

# ------------------------------------------------------------------------------
#
# Target that prints the help
#
help:
	@echo "DEBUG help in board-images-category.makdefile"
	@echo "Available targets are :"
	@echo "   list-images             Display the liste of images available in this category."
	@echo "                           The following filters can be used to display only matching images : "
	@echo "                           arch=(armv7l,aarch64,x86_64 or any valid arch from uname -m)."
	@echo "                           type=(rootfs or firmware)."
	@echo "   sanity-check            Check the availability of required items (files, symlinks, directories)"
	@echo "                           In the following subdirs $(CHECK_FOR_SANITY)."
	@echo "                           This target only warns you and do not make any change to the tree content."
	@echo "   help                    Display this help"
	@echo ""
	@echo "The existing local targets are the following. Local targets are executed only at this"
	@echo "level in the category, without recursion nor walk down the tree of board categories"
