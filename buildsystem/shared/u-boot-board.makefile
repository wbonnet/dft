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

# Include the board definition
include board.mk

PACKAGE_DATE = $(shell LC_ALL=C date +"%a, %d %b %Y %T %z")
PACKAGE_DATE = $(shell date)
HOST_ARCH    = $(shell uname -m)
DFT_HOME     = ../../../../..

# Do not recurse the following subdirs
MAKE_FILTERS  = ./patches ./defconfig . ./files board.mk

# ------------------------------------------------------------------------------
#
# Targets not associated with a file (aka PHONY)
#
.PHONY: help

ifneq ($(name), "")
NEW_VERSION = $(name)
endif
$(info Using DFT installed in $(DFT_HOME))

# ------------------------------------------------------------------------------
#
# Create a new u-boot version entry for the given board
#
new-version:
	@if [ "$(NEW_VERSION)" = "" ] ; then \
		echo "new version name is not defined. Please use name=NEW_VERSION_TO_ADD" ; \
		echo "exit 608" ; \
        exit 1 ; \
        fi ; 
	@if [ -d "./$(NEW_VERSION)" ] ; then \
            echo "Version directory ./($(NEW_VERSION) already exist. Nothing to do... Now returning false to stop execution with an error." ; \
			echo "exit 665" ; \
            exit 1 ; \
        else \
                echo ". Creating the new u-boot version directory (./$(NEW_VERSION))" ; \
                mkdir -p $(NEW_VERSION) ; \
                ln -s ../../../../../buildsystem/shared/u-boot-version.makefile $(NEW_VERSION)/Makefile ; \
                ln -s ../../../../../buildsystem $(NEW_VERSION)/ ; \
                mkdir -p files ; \
                mkdir -p $(NEW_VERSION)/patches ; \
                touch $(NEW_VERSION)/patches/.gitkeep ; \
                cp -fr ../../../../buildsystem/templates/u-boot-package $(NEW_VERSION)/debian ; \
                cd $(NEW_VERSION)/debian ; \
                mv u-boot.install   u-boot-$(BOARD_NAME).install ; \
                cd ../.. ; \
                find $(NEW_VERSION)/debian -type f | xargs sed -i -e "s/__SW_VERSION__/$(NEW_VERSION)/g" \
                                                 -e "s/__BOARD_NAME__/$(BOARD_NAME)/g" \
                                                 -e "s/__DATE__/$(shell LC_ALL=C date +"%a, %d %b %Y %T %z")/g" ; \
        	if [ "${DEBEMAIL}" = "" ] ; then \
                        find $(NEW_VERSION)/debian -type f | xargs sed -i -e "s/__MAINTAINER_EMAIL__/unknown/g" ; \
                else \
                        find $(NEW_VERSION)/debian -type f | xargs sed -i -e "s/__MAINTAINER_EMAIL__/${DEBEMAIL}/g" ; \
		fi ; \
		if [ "${DEBFULLNAME}" = "" ] ; then \
			find $(NEW_VERSION)/debian -type f | xargs sed -i -e "s/__MAINTAINER_NAME__/unknown/g" ; \
		else \
			find $(NEW_VERSION)/debian -type f | xargs sed -i -e "s/__MAINTAINER_NAME__/${DEBFULLNAME}/g" ; \
		fi ; \
		echo "git add $(NEW_VERSION)" ; \
	fi ;

check:
	@echo "Checking u-boot packages definition for board $(BOARD_NAME)" ;
	@if [ -f "$(BOARD_NAME).mk" ] ; then \
		echo "file $(BOARD_NAME).mk should no longer exist in the repo it is now replaced by board.mk" ; \
		echo "please check that information in board.mk are up to date and remove the obsolete file with the following command :" ; \
		echo "git rm -f $(shell pwd)/$(BOARD_NAME).mk" ; \
		echo "exit 609" ; \
		exit 1 ; \
	fi ;
	@if [ ! -f "./board.mk" ] ; then \
		echo "file board.mk is missing in directory $(shell pwd)" ; \
		echo "exit 654" ; \
		exit 1 ; \
	fi ;
	@if [ ! -L "./buildsystem" ] ; then \
		echo "buildsystem symlink to ../../../../../buildsystem is missing in $(shell pwd) You are using your own custom buildsystem." ; \
		echo "exit 602" ; \
		echo "You can fix with the following commands : " ; \
		echo "ln -s ../../../../buildsystem $(shell pwd)" ; \
		echo "git add $(shell pwd)/buildsystem " ; \
		exit 1 ; \
	fi ;
	@if [ ! "$(shell readlink ./buildsystem)" = "../../../../buildsystem" ] ; then \
		echo "target of symlink buildsystem should be ../../../../buildsystem in directory $(shell pwd) You are using your own custom buildsystem." ; \
		echo "exit 603" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f buildsystem " ; \
		echo "ln -s ../../../../../buildsystem $(shell pwd)" ; \
		echo "git add $(shell pwd)/buildsystem " ; \
		exit 1 ; \
	fi ;
	@if [ ! -L "./Makefile" ] ; then \
		echo "Makefile symlink to ../../../../../buildsystem/shared/u-boot-board.makefile is missing in $(shell pwd). You are using your own custom Makefile." ; \
		echo "exit 604"\
		exit  1 ; \
	fi ; 
	@if [ ! "$(shell readlink ./Makefile)" = "../../../../buildsystem/shared/u-boot-board.makefile" ] ; then \
		echo "target of symlink Makefile should be ../../../../buildsystem/shared/u-boot-board.makefile in directory $(shell pwd) You are using your own custom buildsystem." ; \
		echo "exit 605" ; \
		exit 1 ; \
	fi ;
	@for i in $(filter-out $(MAKE_FILTERS),$(shell find . -maxdepth 1 -type d )) ; do \
		cd $$i ; \
		if [ ! -e "buildsystem" ] ; then \
			echo "buildsystem symlink to ../../../../../buildsystem is missing in $(shell pwd) You are using your own custom buildsystem" ; \
			echo "You can fix with the following commands : " ; \
			echo "ln -s ../../../../../buildsystem $(shell pwd)/$$i" ; \
			echo "git add $(shell pwd)/$$i/buildsystem $(shell pwd)/buildsystem" ; \
			echo "exit 661" ; \
			exit 1 ; \
		fi ; \
		if [ ! -e "Makefile" ] ; then \
			echo "Makefile symlink to ../../../../../buildsystem/shared/u-boot-version.makefile is missing in $(shell pwd)/$$i" ; \
			echo "exit 653" ; \
			echo "You can fix with the following commands : " ; \
			echo "git rm -f $(shell pwd)/$$i/Makefile  " ; \
			echo "ln -s ../../../../../buildsystem/shared/u-boot-version.makefile $(shell pwd)/$$i/Makefile " ; \
			echo "git add $(shell pwd)/$$i/Makefile  " ; \
			exit 1 ; \
		fi ; \
		if [ ! -d "$(shell pwd)/files" ] ; then \
			echo "Directory files is missing under $(shell pwd)/" ; \
			echo "It should contain a symlink to the markdown file describing u-boot installation produre for $(BOARD_NAME)" ; \
			echo "You can fix with the following commands : " ; \
			echo "mkdir $(shell pwd)/$$i/files  " ; \
			echo "ln -s ../../files/install.$(BOARD-NAME).orangepi-r1.md $(shell pwd)/$$i/files/install.u-boot.$(BOARD_NAME).md " ; \
			echo "git add $(shell pwd)/$$i/files/install.u-boot.$(BOARD_NAME).md " ; \
			echo "exit 663" ; \
			exit 1 ; \
		fi ; \
		if [ ! -e "$(shell pwd)/files/install.u-boot.$(BOARD_NAME).md" ] ; then \
			echo "Instalation procedure symlink is missing under $(shell pwd)//files" ; \
			echo "This folder should contain a symlink to the markdown file describing u-boot installation produre for $(BOARD_NAME)" ; \
			echo "You can fix with the following commands : " ; \
			echo "ln -s ../../files/install.u-boot.$(BOARD_NAME).md $(shell pwd)/$$i/files/install.u-boot.$(BOARD_NAME).md " ; \
			echo "git add $(shell pwd)/$$i/files/install.u-boot.$(BOARD_NAME).md " ; \
			echo "exit 664" ; \
			exit 1 ; \
		fi ; \
		$(MAKE) $@ || exit 12 ; \
		cd .. ; \
	done ; \

# Catch all target. Call the same targets in each subfolder
%:
	@for i in $(filter-out $(MAKE_FILTERS),$(shell find . -maxdepth 1 -type d )) ; do \
		if [ -d $$i ] ; then \
			cd $$i ; \
			echo "$(MAKE) $@ || exit 13" ; \
			$(MAKE) $@ || exit 13 ; \
			cd .. ; \
			else \
			echo "$$i  nest pas un repertoire  j'en fais quoi ?" ; \
		fi ; \
	done

# ------------------------------------------------------------------------------
#
# Target that prints the help
#
help :
	@echo "Available targets are :" ; \
	echo "   new-version name=VERSION   Create a new version entry. ex: make new-version name=2019.10" ; \
	echo "                              This target will create a subdirectory named 2019.10 containing" ; \
	echo "                              the Makefile and all the files needed to fetch and build given" ; \
	echo "                              version. It also instanciate package template."
