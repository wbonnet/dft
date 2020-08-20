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
MAKE_FILTERS  = Makefile README.md . inc sbit

# definition of the board categories to process
CATEGORIES    = laptop desktop devkit set-top-box single-board-computer phone tablet

# Simple target forwarder
list-images:
sanity-check:
	@for category in $(CATEGORIES) ; do \
		if [ ! -d ${CURDIR}/$$category ] ; then \
			echo "Warning : $$category folder is missing, recursive targets may fail or produce incomplete set of binaries." ; \
		fi ; \
		if [ ! -e "${CURDIR}/$$category/buildsystem" ] ; then \
			echo "buildsystem symlink in ${CURDIR}/$$category is missing or target does not exist. It should be a symlink to ../buildsystem" ; \
			echo "You can fix with the following shell commands :" ; \
			echo "ln -s ../buildsystem ${CURDIR}/$$category/buildsystem" ; \
			echo "git add ${CURDIR}/$$category/buildsystem" ; \
			$(call dft_error ,200103-01) ; \
		fi ; \
		if [ ! $(shell readlink ${CURDIR}/$$category/buildsystem) = "../$(DFT_BUILDSYSTEM)" ] ; then \
			echo "buildsystem symlink in ${CURDIR}/$$category must link to ../$(DFT_BUILDSYSTEM)" ; \
			echo "It targets to $(shell readlink ${CURDIR}/$$category/buildsystem)" ; \
			echo "You can fix with the following shell commands :" ; \
			echo "git rm -f ${CURDIR}/$$category/buildsystem" ; \
			echo "ln -s ../buildsystem ${CURDIR}/$$category/buildsystem" ; \
			echo "git add ${CURDIR}/$$category/buildsystem" ; \
			$(call dft_error ,200103-02) ; \
		fi ; \
		if [ ! -e "${CURDIR}/$$category/Makefile" ] ; then \
			echo "Makefile symlink in ${CURDIR}/$$category is missing or target does not exist. It should be a symlink to ../buildsystem/category.makefile" ; \
			echo "You can fix with the following shell commands :" ; \
			echo "ln -s ../$(buildsystem)/category.makefile $$category/Makefile" ; \
			echo "git add ${CURDIR}/$$category/Makefile" ; \
			$(call dft_error ,1091102-01) ; \
		fi ; \
		if [ ! $(shell readlink ${CURDIR}/$$category/Makefile) = "../$(buildsystem)/category.makefile" ] ; then \
			echo "Makefile symlink in ${CURDIR}/$$category must link to ../$(buildsystem)/category.makefile" ; \
			echo "It targets to $(shell readlink ${CURDIR}/$$category/Makefile)" ; \
			$(call dft_error ,191103-01) ; \
		fi ; \
		if [ -f ${CURDIR}/$$category/Makefile ] ; then \
			$(MAKE) --no-print-directory --directory=$$category sanity-check ; \
		else  \
			echo "DEBUG: Makefile is missing in ${CURDIR}/$$category" ; \
		fi ; \
		for board in `find $$category -mindepth 1 -maxdepth 1 -type d | tr / \  | cut --delimiter=\  --fields=2` ; do \
			if [ ! -f sbit/$$board.sbit.yml ] ; then \
				pwd ; \
				echo "Missing image XXX support tests description file sbit/$$board.sbit.yml" ; \
				$(call dft_error ,200819-01) ; \
				fi ; \
	  done ; \
		if [ ! -d ${CURDIR}/$$category ] ; then \
			echo "Warning : $$category folder is missing, recursive targets may fail or produce incomplete set of binaries." ; \
		fi ; \
	done





















	@for v in $(filter-out $(MAKE_FILTERS),$(shell find .  -mindepth 1 -maxdepth 1 -type d -printf '%P\n')) ; do \
		if [ ! -e "$$v/buildsystem" ] ; then \
			echo "buildsystem symlink ${CURDIR}/$$v/buildsystem is Missing. It should be a symlink to ../buildsystem" ; \
			echo "You can fix with the following shell commands :" ; \
			echo "ln -s ../buildstem ${CURDIR}/$$v/buildsystem" ; \
			echo "git add ${CURDIR}/$$v/buildsystem" ; \
			$(call dft_error ,2005-0201) ; \
		fi ; \
		if [ -f ${CURDIR}/$$v/Makefile ] ; then \
			$(MAKE) --directory=$$v $@ ; \
		fi ; \
		for board in `find $$category -mindepth 1 -maxdepth 1 -type d | tr / \  | cut --delimiter=\  --fields=2` ; do \
			if [ ! -f sbit/$$board.sbit.yml ] ; then \
				echo "Missing board support tests description file sbit/$$board.sbit.yml" ; \
				$(call dft_error ,200819-01) ; \
				fi ; \
	  done ; \



	done

# ------------------------------------------------------------------------------
#
# Target that prints the help
#
help:
	@echo "DEBUG help in board-images top level makefile"
	@echo "Available targets are :"
	@echo "   list-images             Display the liste of images available in this category."
	@echo "                           The following filters can be used to display only matching images : "
	@echo "                           arch=(armv7l,aarch64,x86_64 or any valid arch from uname -m)."
	@echo "                           type=(rootfs or firmware)."
	@echo "   sanity-check            Check recursivly the availability of required items (files, symlinks, directories)"
	@echo "                           This target only warns you and do not make any change to the tree content."
	@echo "   help                    Display this help"
