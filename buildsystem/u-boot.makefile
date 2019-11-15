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

$(info "D3BUG u-boot.makefile")
buildsystem := ../../../../buildsystem
$(warning "review in progress u-boot.makefile")
include board.mk

# Do not recurse the following subdirs
MAKE_FILTERS  = Makefile README.md .

# 
# Board level u-boot makefile
#

check :
	@echo "Checking u-boot folder for board $(BOARD_NAME)" 
	@if [ ! -L "Makefile"  ] ; then \
		echo "Makefile symlink $(buildsystem)/u-boot.makefile is missing in directory $(shell pwd)" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f $(shell pwd)/Makefile" ; \
		echo "ln -s $(buildsystem)/u-boot.makefile $(shell pwd)/Makefile" ; \
		echo "git add $(shell pwd)/Makefile" ; \
		echo "error 1911115-02" ; \
		exit 1 ; \
	fi ;
	@if [ ! "$(shell readlink Makefile)" = "$(buildsystem)/u-boot.makefile" ] ; then \
		echo "target of symlink Makefile should be $(buildsystem)/u-boot.makefile in directory $(shell pwd)" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f $(shell pwd)/Makefile" ; \
		echo "ln -s $(buildsystem)/u-boot.makefile $(shell pwd)/Makefile" ; \
		echo "git add $(shell pwd)/Makefile" ; \
		echo "error 1911115-01" ; \
		exit 1 ; \
	fi ;
	@if [ ! -d "files" ] ; then \
		echo "directory files is missing in u-boot version directory $(shell pwd)" ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir -p files" ; \
		echo "touch files/.gitkeep" ; \
		echo "git add files/.gitkeep" ; \
		echo "error 1911115-03" ; \
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
	for version in $(shell find . -mindepth 1 -maxdepth 1 -type d  -name '201*' ) ; do \
		if [ ! -L "$$version/Makefile" ] ; then \
			echo "Makefile in $(shell pwd)/$$version is missing. It should be a symlink to $(buildsystem)/u-boot-version.makefile" ; \
			echo "You can fix with the following shell commands :" ; \
			echo "ln -s ../$(buildsystem)/u-boot-version.makefile $$version/Makefile" ; \
			echo "git add $$version/Makefile" ; \
			echo "exit 191115-07" ; \
			exit 1 ; \
		fi ; \
		s=`readlink $$version/Makefile` ; \
		if [ !  "$$s" = "../$(buildsystem)/u-boot-version.makefile" ] ; then \
			echo "Makefile symlink in $$version must link to $(buildsystem)/u-boot-version.makefile" ; \
			echo "You can fix with the following shell commands :" ; \
			echo "git rm -f $$version/Makefile || rm -f $$version/Makefile" ; \
			echo "ln -s ../$(buildsystem)/u-boot-version.makefile $$version/Makefile" ; \
			echo "git add $$version/Makefile" ; \
			echo "exit 191115-09" ; \
			exit 1 ; \
		fi ; \
	done ; \

help :
	@echo "Supported targets are"
	@echo 'check : Verify the availability of required items (files, symlinks, directories) and report missing.'
