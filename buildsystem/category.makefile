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

.PHONY: help

buildsystem := ../../buildsystem
include $(buildsystem)/inc/linux-kernel.mk
include $(buildsystem)/dft.mk

# Do not recurse the following subdirs
MAKE_FILTERS  = Makefile workdir README.md .
SW_NAME       = SW_NAME_undefined_at_category_level

# Board category directory contains several folders, on per board in this category
# Each board folder must contain a board.mk file with board specific information, 
# a mandatory kernel folder, optional folders like u-boot for boot loader and files 
# to store needed additionnal files
sanity-check:
	@for board in $(shell find . -mindepth 1 -maxdepth 1 -type d ) ; do \
		if [ ! -e "$$board/Makefile" ] ; then \
			echo "Makefile in ${CURDIR}/$$board is Missing. It should be a symlink to  $(buildsystem)/board.makefile" ; \
			echo "You can fix with the following shell commands :" ; \
			echo "git rm -f $$board/Makefile" ; \
			echo "ln -s $(buildsystem)/board.makefile ${CURDIR}/$$board/Makefile" ; \
			echo "git add $$board/Makefile" ; \
			echo "exit 101101" ; \
			exit 1 ; \
		fi ; \
		s=`readlink $$board/Makefile` ; \
		if [ !  "$$s" = "../$(buildsystem)/board.makefile" ] ; then \
			echo "Makefile symlink in $$board must link to $(buildsystem)/board.makefile" ; \
			echo "It targets to $$s" ; \
			echo "exit 825" ; \
			exit 1 ; \
		fi ; \
		if [ ! -f $$board/board.mk ] ; then \
			echo "Board description file board.mk is missing in directory ${CURDIR}//$$board" ; \
			echo "You can fix with the following shell commands :" ; \
			echo "git rm -f $$board/Makefile" ; \
			echo "cp  $(buildsystem)/board.mk.template ${CURDIR}//$$board/board.mk" ; \
			echo "git add ${CURDIR}//$$board/board.mk" ; \
			echo "Warning !!! : Don't forget to edit this file and replace 'unkown' values with board specific values" ; \
			echo "exit 191117-01" ; \
			exit 1 ; \
		fi ; \
	done ; \
	for folder in $(shell find . -mindepth 1 -maxdepth 1 -type d ) ; do \
		if [ -f $$folder/Makefile ] ; then \
			cd $$folder && $(MAKE) sanity-check && cd .. ; \
		fi ; \
	done ;

# If package is called then make both u-boot and kernel-package
package: bsp-package
bsp: bsp-package
bsp-package: u-boot-package kernel-package 

# Build only u-boot package target
u-boot-package:
	@for i in $(filter-out $(MAKE_FILTERS),$(shell find . -mindepth 1 -maxdepth 1 -type d )) ; do \
		if [ -f $$i/Makefile ] ; then \
			cd $$i && $(MAKE) u-boot-package && cd .. ; \
		fi ; \
        done

# Build only linux kernel an package target
kernel-package:
	@for i in $(filter-out $(MAKE_FILTERS),$(shell find . -mindepth 1 -maxdepth 1 -type d )) ; do \
		if [ -f $$i/Makefile ] ; then \
			cd $$i && $(MAKE) kernel-package && cd .. ; \
		fi ; \
        done

# Catch all target. Call the same targets in each subfolder
%:
	@for i in $(filter-out $(MAKE_FILTERS),$(shell find . -mindepth 1 -maxdepth 1 -type d )) ; do \
		if [ -f $$i/Makefile ] ; then \
			cd $$i && $(MAKE) $@ && cd .. ; \
		fi ; \
        done
