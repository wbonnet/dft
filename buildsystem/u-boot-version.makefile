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

$(info "D3BUG u-boot-version.makefile")
buildsystem := ../../../../../buildsystem
$(warning "review in progress u-boot-version.makefile")

# Do not recurse the following subdirs
MAKE_FILTERS  = Makefile README.md .

# Include board specific definitions  from board level
include ../../board.mk

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

# u-boot version folder must contain a symlink to the buildsystem and a debiani
# folder storing debian package definition
 
check :

# board level directory must contain the board.mk file
	@echo "Checking board definition for $(BOARD_NAME)" ;
	@if [ ! -f "board.mk" ] ; then \
		pwd ; \
		echo "file board.mk is missing in directory $(shell pwd)" ; \
		echo "error 191112-01" ; \
		exit 1 ; \
	fi ;
	@if [ ! -d "$(shell pwd)/kernel" ] ; then \
		echo "kernel directory is missing in $(shell pwd). It should contains a symlink to the generic makefile for Linux kernel" ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir $(shell pwd)/kernel" ; \
		echo "ln -s $(buildsystem)/linux-kernel.makefile $(shell pwd)/kernel/Makefile" ; \
		echo "git add $(shell pwd)/kernel" ; \
		echo "error 191114-01" ; \
		exit 1 ; \
	fi ;
	@if [ ! -d "$(shell pwd)/kernel/defconfig" ] ; then \
		echo "defconfig directory is missing in $(shell pwd). It is used to store kernel configuration files. It should at leasty contains a hidden empty file .gitkeep until first kernel version is added" ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir $(shell pwd)/kernel/defconfig" ; \
		echo "touch $(shell pwd)/kernel/defconfig/.gitkeep" ; \
		echo "git add $(shell pwd)/kernel/defconfig" ; \
		echo "error 191114-01" ; \
		exit 1 ; \
	fi ;
	@if [ ! -d "$(shell pwd)/u-boot" ] ; then \
		echo "u-boot directory is missing in $(shell pwd). It should contains a symlink to the generic makefile for u-boot" ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir $(shell pwd)/u-boot" ; \
		echo "ln -s $(buildsystem)/u-boot.makefile $(shell pwd)/u-boot/Makefile" ; \
		echo "git add $(shell pwd)/u-boot" ; \
		echo "error 191114-02" ; \
		exit 1 ; \
	fi ;
	@if [ ! -d "$(shell pwd)/files" ] ; then \
		echo "files directory is missing in $(shell pwd). It should contains the markdown file install.$(SRC_NAME).$(BOARD_NAME).md needed by target package." ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir $(shell pwd)/files" ; \
		echo "ln -s ../../files/install.$(SRC_NAME).$(BOARD_NAME).md $(shell pwd)/files/" ; \
		echo "git add $(shell pwd)/files" ; \
		echo "error 191112-02" ; \
		exit 1 ; \
	fi ;

# Catch all target. Call the same targets in each subfolder
%:
	@for i in $(filter-out $(MAKE_FILTERS),$(shell find . -maxdepth 1 -type d )) ; do \
                $(MAKE) -C $$i $* || exit 1 ; \
        done


help :
	@echo "Supported targets are"
	@echo 'check : Verify the availability of required items (files, symlinks, directories) and report missing.'


	@echo "Checking u-boot version $(SW_VERSION) package definition for $(BOARD_NAME)" 
	@if [ ! -f "../board.mk" ] ; then \
		echo "file board.mk is missing in directory $(shell pwd)/.." ; \
		false ; \
	fi ;
	@if [ ! -d "$(shell pwd)/files" ] ; then \
		echo "files directory is missing in $(shell pwd). It should contains the markdown file install.$(SRC_NAME).$(BOARD_NAME).md needed by target package." ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir $(shell pwd)/files" ; \
		echo "ln -s ../../files/install.$(SRC_NAME).$(BOARD_NAME).md $(shell pwd)/files/" ; \
		false ; \
	fi ;
	@if [ ! -d "./debian" ] ; then \
		echo "debian directory is missing in $(shell pwd). It should contains the files needed to create the debian package for $(BOARD_NAME) u-boot." ; \
		false ; \
	fi ;
	@if [ ! -L "files/install.$(SRC_NAME).$(BOARD_NAME).md" ] ; then \
		echo "Installation procedure symlink is missing under $(shell pwd)/files" ; \
		echo "This folder should contain a symlink to the markdown file describing u-boot installation produre for $(BOARD_NAME)" ; \
		echo "You can fix with the following commands : " ; \
		echo "ln -s ../../files/install.u-boot.$(BOARD_NAME).md $(shell pwd)/files/install.u-boot.$(BOARD_NAME).md" ; \
		echo "git add $(shell pwd)/files/install.u-boot.$(BOARD_NAME).md" ; \
		exit 1 ; \
	fi ;
	@if [ ! -L "./Makefile" ] ; then \
		echo "Makefile symlink to ../../../../../buildsystem/shared/u-boot-version.makefile is missing in $(shell pwd)" ; \
		false ; \
	fi ; 
	@if [ ! -L "./buildsystem" ] ; then \
		echo "buildsystem symlink to ../../../../../buildsystem is missing in $(shell pwd). You are using your own custom buildsystem" ; \
		false ; \
	fi ;
	@if [ ! "$(shell readlink ./buildsystem)" = "../../../../../buildsystem" ] ; then \
		echo "target of symlink buildsystem should be ../../../../../buildsystem in directory $(shell pwd)" ; \
		false ; \
	fi ;
	@if [ ! "$(shell readlink ./Makefile)" = "../../../../../buildsystem/shared/u-boot-version.makefile" ] ; then \
		echo "target of symlink Makefile should be ../../../../../buildsystem/shared/u-boot-version.makefile in directory $(shell pwd)" ; \
		false ; \
	fi ;
	
help :
	@echo "Supported targets are"
	@echo 'check : Verify the availability of required items (files, symlinks, directories) and report missing.'
