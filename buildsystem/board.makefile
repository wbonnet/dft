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

$(info "D3BUG board.makefile")
buildsystem := ../../../buildsystem
$(warning "review in progress board.makefile")

# 
# Board level generic Makefile
#

# No need to recurse check target at version level
check :
# Board level directory must contain board.mk file, kernel folder and u-boot folder
# Mandatory folders content check (otherwise recusive targets may not work)

# kernel folder must contain a Makefile symlink to  ../../../../buildsystem/shared/board-kernel.makefile
# Board level directory must contain board.mk file, kernel folder and u-boot folder
	@echo "Checking u-boot version $(SW_VERSION) package definition for $(BOARD_NAME)" ;
	for folder in $(shell find . -maxdepth 1 -type d ) ; do \
		echo "folder : $$folder" ; \
	done ;
	@if [ ! -f "board.mk" ] ; then \
		pwd ; \
		echo "file board.mk is missing in directory $(shell pwd)" ; \
		echo "error 191112-01" ; \
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
	@if [ ! -d "./debian" ] ; then \
		echo "debian directory is missing in $(shell pwd). It should contains the files needed to create the debian package for $(BOARD_NAME) u-boot." ; \
		echo "error 191112-03" ; \
		exit 1 ; \
	fi ;
	@if [ ! -L "files/install.$(SRC_NAME).$(BOARD_NAME).md" ] ; then \
		echo "Installation procedure symlink is missing under $(shell pwd)/files" ; \
		echo "This folder should contain a symlink to the markdown file describing u-boot installation produre for $(BOARD_NAME)" ; \
		echo "You can fix with the following commands : " ; \
		echo "ln -s ../../files/install.u-boot.$(BOARD_NAME).md $(shell pwd)/files/install.u-boot.$(BOARD_NAME).md" ; \
		echo "git add $(shell pwd)/files/install.u-boot.$(BOARD_NAME).md" ; \
		echo "error 191112-04" ; \
		exit 1 ; \
	fi ;
	@if [ ! -L "./Makefile" ] ; then \
		echo "Makefile symlink to $(buildsystem)/u-boot-version.makefile is missing in $(shell pwd)" ; \
		echo "error 191112-09" ; \
		exit 1 ; \
	fi ; 
	@if [ ! -L "./buildsystem" ] ; then \
		echo "buildsystem symlink to $(buildsystem)is missing in $(shell pwd). You are using your own custom buildsystem" ; \
		echo "error 191112-05" ; \
		exit 1 ; \
	fi ;
	@if [ ! "$(shell readlink ./buildsystem)" = "$(buildsystem)" ] ; then \
		echo "target of symlink buildsystem should be $(buildsystem) in directory $(shell pwd)" ; \
		echo "error 191112-06" ; \
		exit 1 ; \
	fi ;
	@if [ ! "$(shell readlink ./Makefile)" = "$(buildsystem)/u-boot-version.makefile" ] ; then \
		echo "target of symlink Makefile should be $(buildsystem)/u-boot-version.makefile in directory $(shell pwd)" ; \
		echo "error 191112-07" ; \
		exit 1 ; \
	fi ;

help :
	@echo "Supported targets are"
	@echo 'check : Verify the availability of required items (files, symlinks, directories) and report missing.'
