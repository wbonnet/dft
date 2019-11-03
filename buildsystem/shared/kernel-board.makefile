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
MAKE_FILTERS = defconfig/
HOST_ARCH    = $(shell uname -m)
DFT_HOME    ?= $(shell pwd)

# ------------------------------------------------------------------------------
#
# Targets not associated with a file (aka PHONY)
#
.PHONY: help

ifdef name
    NEW_VERSION = $(name)
else
    $(error Parameter name is missing. Please provide the kervel version to add using make new-version name=x.y.z)
endif

    $(info Using DFT installed in $(DFT_HOME))

# ------------------------------------------------------------------------------
#
# Create a new kernel version entry for the given board
#
new-version:
	if [ "$(DFT_HOME)" = "" ] ; then \
		echo "DFT_HOME environment variable is empty. Please define it in the shell environment used to run the make command. It can be done by setting DFT_HOME path in your shell config file or before the make command" ; \
		echo "ie: DFT_HOME=/path/to/somewhere make name=$(NEW_VERSION)" ; \
	fi ; \
	if [ ! -d "$(DFT_HOME)/buildsystem" ] ; then \
		echo "Error : builsystem directory was not found. The buildsystem has to be available under the path defined by the DFT_HOME environment variable."; \
		echo "DFT_HOME is currently set in your shell to : $(DFT_HOME)";\
		echo "You should check the DFT_HOME definition in your environment config file or set it on the make commande line" ;\
		echo "ie: DFT_HOME=/path/to/somewhere make name=$(NEW_VERSION)" ; \
	fi ;\
	if [ -d "./$(NEW_VERSION)" ] ; then \
		echo "Version directory ./($(NEW_VERSION) already exist. Nothing to do... Now returning false to stop execution with an error." ; \
		false ; \
	else \
		echo ". Creating the new kernel version directory (./$(NEW_VERSION))" ; \
		mkdir -p $(NEW_VERSION) ; \
		ln -s $(DFT_HOME)/../buildsystem/shared/kernel-version-level.makefile $(NEW_VERSION)/Makefile ; \
		ln -s $(DFT_HOME)/../buildsystem $(NEW_VERSION)/buildsystem ; \
		mkdir -p files ; \
		mkdir -p $(NEW_VERSION)/patches ; \
		touch $(NEW_VERSION)/patches/.gitkeep ; \
		cp -fr $(DFT_HOME)/buildsystem/templates/kernel-package $(NEW_VERSION)/debian ; \
		cd $(NEW_VERSION)/debian ; \
		mv linux-kernel.postinst  linux-kernel-$(BOARD_NAME).postinst ; \
		mv linux-kernel.postrm    linux-kernel-$(BOARD_NAME).postrm ; \
		mv linux-kernel.preinst   linux-kernel-$(BOARD_NAME).preinst ; \
		mv linux-kernel.prerm     linux-kernel-$(BOARD_NAME).prerm ; \
		mv linux-kernel.install   linux-kernel-$(BOARD_NAME).install ; \
		mv linux-headers.install  linux-headers-$(BOARD_NAME).install ; \
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
		git add $(NEW_VERSION) ; \
	fi ;

# ------------------------------------------------------------------------------
#
# Target that prints the help
#
help :
	@echo "Available targets are :"
	@echo '   new-version name=VERSION   Create a new version entry. ex: make new-version name=4.15.3'
	@echo '                              This target will create a subdirectory named 4.15.3, containing'
	@echo '                              the Makefile and all the files needed to fetch and build given'
	@echo '                              version. It also instanciate package template.'

# Catch all target. Call the same targets in each subfolder
%:
	@for i in $(filter-out $(MAKE_FILTERS),$(wildcard */)) ; do \
		$(MAKE) -C $$i $* || exit 1 ; \
	done

