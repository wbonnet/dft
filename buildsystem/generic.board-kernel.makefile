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
PACKAGE_DATE = $(shell date )
FILTER_DIRS  = files/
HOST_ARCH    = $(shell uname -m)

# ------------------------------------------------------------------------------
#
# Targets not associated with a file (aka PHONY)
#
.PHONY: help

# Create a new board entry in the repository
new-version:
	@if [ "x${DFT_HOME}" = "x" ] ; \
	then \
	echo "DFT_HOME variable is not set in your shell environment. Please define it interactively or in your shell configuration file (reloading it). For instance with the following command or equivalent\n" ; \
		echo "export DFT_HOME=/path/to/dft/makefiles" ; \
		false ; \
	else  \
		echo ". Creating the directory structure (./$(VERSION))" ; \
		mkdir -p $(VERSION) ; \
		cp -f ${DFT_HOME}/buildsystem/kernel-version.makefile $(VERSION)/Makefile ; \
		ln -s ${DFT_HOME}/buildsystem/ $(VERSION)/buildsystem ; \
		mkdir -p $(VERSION)/files ; \
		ln -s ../../config_files/default.$(BOARD_NAME).config $(VERSION)/files/$(BOARD_NAME).config ; \
		mkdir -p $(VERSION)/patches ; \
		touch $(VERSION)/patches/.gitkeep ; \
		echo "work-$(BOARD_NAME)/" > $(VERSION)/.gitignore ; \
		sed -i -e "s/__KERNEL_VERSION__/$(VERSION)/g" $(VERSION)/Makefile ; \
		cp -fr ${DFT_HOME}/buildsystem/templates/debian.kernel $(VERSION)/debian; \
		cd $(VERSION)/debian ; \
		mv linux-image.postinst  linux-image-$(BOARD_NAME).postinst ; \
		mv linux-image.postrm    linux-image-$(BOARD_NAME).postrm ; \
		mv linux-image.preinst   linux-image-$(BOARD_NAME).preinst ; \
		mv linux-image.prerm     linux-image-$(BOARD_NAME).prerm ; \
		mv linux-image.install   linux-image-$(BOARD_NAME).install ; \
		mv linux-headers.install linux-headers-$(BOARD_NAME).install ; \
		cd ../.. ; \
		find $(VERSION)/debian -type f | xargs sed -i -e "s/__KERNEL_VERSION__/$(VERSION)/g" \
	                                         -e "s/__BOARD_NAME__/$(BOARD_NAME)/g" \
	                                         -e "s/__DATE__/$(shell LC_ALL=C date +"%a, %d %b %Y %T %z")/g" ; \
        if [ "${DEBEMAIL}" = "" ] ; then \
			find $(VERSION)/debian -type f | xargs sed -i -e "s/__MAINTAINER_EMAIL__/unknown/g" ; \
		else \
			find $(VERSION)/debian -type f | xargs sed -i -e "s/__MAINTAINER_EMAIL__/${DEBEMAIL}/g" ; \
		fi ; \
		if [ "${DEBFULLNAME}" = "" ] ; then \
			find $(VERSION)/debian -type f | xargs sed -i -e "s/__MAINTAINER_NAME__/unknown/g" ; \
		else \
			find $(VERSION)/debian -type f | xargs sed -i -e "s/__MAINTAINER_NAME__/${DEBFULLNAME}/g" ; \
		fi ; \
		git add $(VERSION) ; \
	fi ;

# Catch all target. Call the same targets in each subfolder
%:
	@for i in $(filter-out $(FILTER_DIRS),$(wildcard */)) ; do \
		$(MAKE) -C $$i $* || exit 1 ; \
	done

# Catch all target. Call the same targets in each subfolder
%:
	@if [ ! "x$(HOST_ARCH)" = "x$(BOARD_ARCH)" ] ; \
	then \
	    echo "Board is $(BOARD_ARCH) and i run on $(HOST_ARCH). Skipping recursive target call..." ; \
	    true ; \
	else \
		for i in $(filter-out $(FILTER_DIRS),$(wildcard */)) ; do \
			$(MAKE) -C $$i $* || exit 1 ; \
		done \
	fi


# ------------------------------------------------------------------------------
#
# Target that prints the help
#
help :
	@echo "Available targets are :"
	@echo '   new-version VERSION=a.b.c Create a new version entry. ex: make new-version VERSION=4.16.8'
	@echo '                             This target will create a subdirectory named after the content of the VERSION variable.'
	@echo '                             It will contain the Makefile and all the files needed to fetch and build the given'
	@echo '                             version. It also instanciate Debian package template.'
