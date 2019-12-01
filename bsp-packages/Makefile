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
# Copyright 2019 DFT project (http://www.debianfirmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#


buildsystem := ../buildsystem
include $(buildsystem)/dft.mk

# Do not recurse the following subdirs
MAKE_FILTERS  = Makefile README.md . kernel-defconfig-fragments

# definition of the liste of boards category 
CATEGORIES    = laptop desktop set-top-box single-board-computer

# ------------------------------------------------------------------------------
#
# Targets not associated with a file (aka PHONY)
#
.PHONY: help

#check que tes subdirs de category ont la et ont un lien makefile valide ensuite ca recurse
sanity-check:
	@for category in $(CATEGORIES) ; do \
		if [ ! -d ${CURDIR}/$$category ] ; then \
			echo "Warning : $$c category folder is missing, recursive targets may fail or produce incomplete set of binaries." ; \
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
			echo "exit 191103-01" ; \
			$(call dft_error ,191103-01) ; \
			exit 1 ; \
		fi ; \
		cd ${CURDIR}/$$category && $(MAKE) sanity-check ; \
	done  

#		cd ${CURDIR}/$$i && $(MAKE) sanity-check ; \
# Build only u-boot  package target
u-boot-package:
	@for i in $(CATEGORIES) ; do \
		if [ -f ${CURDIR}/$$i/Makefile ] ; then \
                cd ${CURDIR}/$$i && $(MAKE) u-boot-package ; \
		fi ; \
        done

# Build only linux kernel an package target
kernel-package:
linux-kernel-package:
	@for i in $(CATEGORIES) ; do \
		if [ -f ${CURDIR}/$$i/Makefile ] ; then \
                cd ${CURDIR}/$$i && $(MAKE) kernel-package ; \
		fi ; \
	done


# Catch all target. Call the same targets in each subfolder
%:
	@for i in $(filter-out $(MAKE_FILTERS),$(shell find . -maxdepth 1 -type d )) ; do \
		cd ${CURDIR}/$$i && $(MAKE) $* ; \
	done
