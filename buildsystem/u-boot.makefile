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
# Copyright 2016 DFT project (http://www.debianfirmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#

# Defines variables specific to u-boot
SW_NAME       = u-boot
SW_VERSION    = SW_VERSION_undefind_at_uboot_level
buildsystem := ../../../../buildsystem
include board.mk
include $(buildsystem)/inc/u-boot.mk

# Do not recurse the following subdirs
MAKE_FILTERS  = files defconfig Makefile README.md patches .

# ------------------------------------------------------------------------------
#
# Targets not associated with a file (aka PHONY)
#
.PHONY: help check

# 
# Board level u-boot makefile
#
sanity-check:
	@echo "Checking u-boot folder sanity for board $(BOARD_NAME)" ;
	@if [ ! -L "Makefile"  ] ; then \
		echo "Makefile symlink $(buildsystem)/u-boot.makefile is missing in directory $(shell pwd)" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f $(shell pwd)/Makefile" ; \
		echo "ln -s $(buildsystem)/u-boot.makefile $(shell pwd)/Makefile" ; \
		echo "git add $(shell pwd)/Makefile" ; \
		echo "error 1911115-02" ; \
		echo "error 1911115-02" ; \
		exit 1 ; \
	fi ;
	@if [ ! "$(shell readlink ./Makefile)" = "$(buildsystem)/u-boot.makefile" ] ; then \
		echo "target of symlink Makefile should be $(buildsystem)/u-boot.makefile in directory $(shell pwd)" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f $(shell pwd)/Makefile" ; \
		echo "ln -s $(buildsystem)/u-boot.makefile $(shell pwd)/Makefile" ; \
		echo "git add $(shell pwd)/Makefile" ; \
		echo "error 1911115-01" ; \
		exit 1 ; \
	fi ;
	@if [ ! -d "$(shell pwd)/files" ] ; then \
		echo "files directory is missing in $(shell pwd). It should contains the markdown file install.u-boot-$(BOARD_NAME).md needed by target package." ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir -p $(shell pwd)/files" ; \
		echo "touch $(shell pwd)/files/.gitkeep" ; \
		echo "ln -s ../../files/install.$(SW_NAME)-$(BOARD_NAME).md $(shell pwd)/files/" ; \
		echo "git add $(shell pwd)/files" ; \
		echo "error 1911115-03" ; \
		exit 1 ; \
	fi ;  
	@if [ ! -d "$(shell pwd)/files" ] ; then \
		echo "You can fix with the following commands : " ; \
		echo "mkdir -p $(shell pwd)/files" ; \
		echo "touch $(shell pwd)/files/.gitkeep" ; \
		echo "git add $(shell pwd)/files" ; \
		echo "error 191112-02" ; \
		exit 1 ; \
	fi ;
	@if [ ! -f "$(shell pwd)/files/install.$(SW_NAME)-$(BOARD_NAME).md" ] ; then \
		ls -lh "$(shell pwd)/files/install.$(SW_NAME)-$(BOARD_NAME).md" ;  \
		echo "the $(SW_NAME) installation procedure is missing in the files/ folder. This folder should contain a file named install.$(SW_NAME)-$(BOARD_NAME).md describing. This file is needed by target package." ; \
		echo "error 191116-01" ; \
		exit 1 ; \
	fi ;
	@if [ ! -L "board.mk" ] ; then \
		echo "board.mk symlink to ../board.mk is missing in directory $(shell pwd)" ; \
		echo "You can fix with the following commands : " ; \
		echo "ln -s ../board.mk board.mk" ; \
		echo "git add board.mk" ; \
		echo "error 1911115-04" ; \
		exit 1 ; \
	fi ;
	@if [ ! "$(shell readlink board.mk)" = "../board.mk" ] ; then \
		echo "target of symlink board.mk should be ../board.mk in directory $(shell pwd)" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f $(shell pwd)/board.mk" ; \
		echo "ln -s ../board.mk $(shell pwd)/board.mk" ; \
		echo "git add $(shell pwd)/board.mk" ; \
		echo "error 1911115-05" ; \
		exit 1 ; \
	fi ;
	@for version in $(shell find . -mindepth 1 -maxdepth 1 -type d -name '*\.*' ) ; do \
         echo "checking version $$version subfolder sanity" ; \
         if [ ! -L "$$version/Makefile" ] ; then \
            echo "Makefile in $(shell pwd)/$$version is missing. It should be a symlink to $(buildsystem)/u-boot-version.makefile" ; \
            echo "You can fix with the following shell commands :" ; \
            echo "ln -s ../$(buildsystem)/u-boot-version.makefile $$version/Makefile" ; \
            echo "git add $$version/Makefile" ; \
            echo "exit 191115-07" ; \
            exit 1 ; \
           fi ; \
           s=`readlink $$version/Makefile` ; \
           echo "readlink retourne $$s" ; \
           if [ !  "$$s" = "../$(buildsystem)/u-boot-version.makefile" ] ; then \
               echo "Makefile symlink in $$version must link to $(buildsystem)/u-boot-version.makefile" ; \
               echo "You can fix with the following shell commands :" ; \
               git rm -f $(shell pwd)/$$version/Makefile || rm -f $(shell pwd)/$$version/Makefile ; \
               ln -s ../$(buildsystem)/u-boot-version.makefile $(shell pwd)/$$version/Makefile ; \
               git add $(shell pwd)/$$version/Makefile ; \
               echo "exit 191122-21" ; \
            fi ; \
	done ; 
	@for version in $(shell find . -mindepth 1 -maxdepth 1 -type d  -name '*\.*' ) ; do \
		if [ -f $$version/Makefile ] ; then \
			echo "make sanity-check in $(SW_NAME) version $(shell pwd)/$$folder" ; \
			$(MAKE) -C $(shell pwd)/$$version sanity-check || exit 1 ; \
		fi ; \
	done ;

# Catch all target. Call the same targets in each subfolder
%:
	for i in $(filter-out $(MAKE_FILTERS),$(shell find . -mindepth 1 -maxdepth 1 -type d )) ; do \
		if [ -f $$i/Makefile ] ; then \
                $(MAKE) -C $$i $* || exit 1 ; \
		fi ; \
        done

help :
	@echo "Supported targets are"
	@echo 'sanity-check : Verify the availability of required items (files, symlinks, directories) and report missing.'
