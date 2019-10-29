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

# Defines the software version
PACKAGE_DATE = $(shell LC_ALL=C date +"%a, %d %b %Y %T %z")
PACKAGE_DATE = $(shell date)
HOST_ARCH    = $(shell uname -m)
DFT_HOME    ?= $(shell pwd)

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
	@if [ "$(DFT_HOME)" = "" ] ; then \
		echo "DFT_HOME environment variable is empty. Please define it in the shell environment used to run the make command. It can be done by setting DFT_HOME path in your shell config file or before the make command" ; \
		echo "ie: DFT_HOME=/path/to/somewhere make name=$(NEW_VERSION)" ; \
	fi ; 
	@if [ ! -d "$(DFT_HOME)/buildsystem" ] ; then \
		echo "Error : builsystem directory was not found. The buildsystem has to be available under the path defined by the DFT_HOME environment variable."; \
		echo "DFT_HOME is currently set in your shell to : $(DFT_HOME)";\
                echo "You should check the DFT_HOME definition in your environment config file or set it on the make commande line" ;\
                echo "ie: DFT_HOME=/path/to/somewhere make name=$(NEW_VERSION)" ; \
                echo "in most os cases you just have to run : export DFT_HOME=../../../.. " ; \
        fi ;
	@if [ "$(NEW_VERSION)" = "" ] ; then \
		echo "new version name is not defined. Please use name=NEW_VERSION_TO_ADD" ; \
                false ; \
        fi ; 
	@if [ -d "./$(NEW_VERSION)" ] ; then \
                echo "Version directory ./($(NEW_VERSION) already exist. Nothing to do... Now returning false to stop execution with an error." ; \
                false ; \
        else \
                echo ". Creating the new u-boot version directory (./$(NEW_VERSION))" ; \
                mkdir -p $(NEW_VERSION) ; \
                ln -s $(DFT_HOME)/../buildsystem/shared/u-boot-version-level.makefile $(NEW_VERSION)/Makefile ; \
                mkdir -p files ; \
                mkdir -p $(NEW_VERSION)/patches ; \
                touch $(NEW_VERSION)/patches/.gitkeep ; \
                cp -fr $(DFT_HOME)/buildsystem/templates/u-boot-package $(NEW_VERSION)/debian ; \
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

# Catch all target. Call the same targets in each subfolder
%:
	@for i in $(filter-out $(FILTER_DIRS),$(wildcard */)) ; do \
		$(MAKE) -C $$i $* || exit 1 ; \
	done

check:
	@if [ ! -f "./board.mk" ] ; then \
		echo "file board.mk is missing in directory $(shell pwd)" ; \
		false ; \
	fi ;
	@if [ ! -L "./buildsystem" ] ; then \
		echo "buildsystem symlink to ../../../../buildsystem is missing in $(shell pwd). You are using your own custom buildsystem." ; \
		false ; \
	fi ;
	@if [ ! "$(shell readlink ./buildsystem)" = "../../../../buildsystem" ] ; then \
		echo "target of symlink buildsystem should be ../../../../buildsystem in directory $(shell pwd). You are using your own custom buildsystem." ; \
		false ; \
	fi ;
	@if [ ! -L "./Makefile" ] ; then \
		echo "Makefile symlink to ../../../../../buildsystem/shared/u-boot-board-level.makefile is missing in $(shell pwd). You are using your own custom Makefile." ; \
		false ; \
	fi ; 
	@if [ ! "$(shell readlink ./Makefile)" = "../../../../buildsystem/shared/u-boot-board-level.makefile" ] ; then \
		echo "target of symlink Makefile should be ../../../../buildsystem/shared/u-boot-board-level.makefile in directory $(shell pwd). You are using your own custom buildsystem." ; \
		false ; \
	fi ;
	@for i in $(filter-out $(FILTER_DIRS),$(wildcard */)) ; do \
		$(MAKE) -C $$i $* || exit 1 ; \
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
