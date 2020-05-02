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
MAKE_FILTERS  = Makefile README.md . inc

# definition of the board categories to process
CATEGORIES    = laptop desktop set-top-box single-board-computer


# Simple target forwarder
list-images:
sanity-check:
	@echo "DEBUG $@ in board-images top level makefile"
	for v in $(filter-out $(MAKE_FILTERS),$(shell find .  -mindepth 1 -maxdepth 1 -type d -printf '%P\n')) ; do \
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
