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
# Copyright 2017 DFT project (http://www.firmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
#
# Even if this work is a complete rewrite, it is originally derivated work based
# upon mGAR build system from OpenCSW project (http://www.opencsw.org).
#
# Copyright 2001 Nick Moffitt: GAR ports system
# Copyright 2006 Cory Omand: Scripts and add-on make modules, except where otherwise noted.
# Copyright 2008 Dagobert Michelsen (OpenCSW): Enhancements to the CSW GAR system
# Copyright 2008-2013 Open Community Software Association: Packaging content
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#

# ------------------------------------------------------------------------------
#
# Protection against multiple include
#
ifdef DFT_TARGET_PACKAGE
$(info target-package.mk has already been included)
else
#$(info now including target-package.mk)
DFT_TARGET_PACKAGE = 1

# Some temporary default values used to debug where where variables are initialized
SW_NAME     ?= no-name-at-target-package
SW_VERSION  ?= no-version-at-target-package

# ------------------------------------------------------------------------------
#
# Execute the package target script
#

# cp $(DFT_BUILDSYSTEM)/templates/u-boot-version.makefile $(PACKAGE_DIR)/Makefile ; \

do-package:
	if [ "$(SW_VERSION)" = "" ] ; then \
		echo "DEBUG : SW_VERSION is empty of undefined. Not at a defined version level skipping do-package" ; \
		exit 0 ; \
	fi ; \
	if [ ! "x$(HOST_ARCH)" = "x$(BOARD_ARCH)" ] ; \
	then \
	    echo "Makefile processing had to be stopped during target $@ execution. The target board is based on $(BOARD_ARCH) architecture and make ris running on a $(HOST_ARCH) board." ; \
	    echo "The generated binaries might be invalid or scripts could fail before reaching the end of target. Cross compilation is not yet supported." ; \
		echo "Processing will now continue only for $(HOST_ARCH) based boards package definitions." ; \
		echo "You can get the missing binaries by running again this target on a $(BOARD_ARCH) based host and collect the generated items." ; \
		echo "To generate binaries for all architectures you will need (for now) several builders, one for each target architecture flavor." ; \
	fi ; \
	if [ ! -f $(COOKIE_DIR)/do-package ] ; then \
		echo "DEBUG le cookie do-package est pas la :) au boulot !" ; \
		echo "DEBUG SW_NAME : $(SW_NAME)"  ; \
		echo "DEBUG je suis dans"  ; \
		pwd ; \
		echo "cd $(BUILD_DIR)/$(SW_NAME)-$(SW_VERSION)" ;  \
		echo "DEBUG et je vais copier le squelette de paquet dans $(PACKAGE_DIR)" ; \
		if [ "$(SW_NAME)" = "linux" ] ; then \
			cp -fr --dereference $(DFT_BUILDSYSTEM)/templates/debian-kernel-package $(PACKAGE_DIR)/debian ; \
			cp --dereference $(DFT_BUILDSYSTEM)/templates/linux-kernel-version.makefile $(PACKAGE_DIR)/Makefile ; \
		else \
			echo DFT_BUILDSYSTEM : $(DFT_BUILDSYSTEM); \
			cp -frv $(DFT_BUILDSYSTEM)/templates/debian-u-boot-package $(PACKAGE_DIR)/debian ; \
			cp -frv --dereference `pwd`/files $(PACKAGE_DIR)/doc ; \
			echo "DEBUG contenu de PACKAGE_DIR $(PACKAGE_DIR)" ; \
			ls -lh $(PACKAGE_DIR) ; \
			echo "DEBUG contenu de PACKAGE_DIR/doc $(PACKAGE_DIR)/doc" ; \
			ls -lh $(PACKAGE_DIR)/doc ; \
		fi ; \
		echo "        running package in $(PACKAGE_DIR)"  ; \
	        if [ "$(DEBEMAIL)" = "" ] ; then \
			find $(PACKAGE_DIR)/debian -type f | xargs sed -i -e "s/__MAINTAINER_EMAIL__/unknown/g" ; \
		else \
			find $(PACKAGE_DIR)/debian -type f | xargs sed -i -e "s/__MAINTAINER_EMAIL__/$(DEBEMAIL)/g" ; \
		fi ; \
		if [ "$(DEBFULLNAME)" = "" ] ; then \
			find $(PACKAGE_DIR)/debian -type f | xargs sed -i -e "s/__MAINTAINER_NAME__/unknown/g" ; \
		else \
			find $(PACKAGE_DIR)/debian -type f | xargs sed -i -e "s/__MAINTAINER_NAME__/$(DEBFULLNAME)/g" ; \
		fi ; \
		sed -i -e "s/__SW_VERSION__/$(SW_VERSION)/g" $(PACKAGE_DIR)/Makefile ; \
		find $(PACKAGE_DIR)/debian -type f | xargs sed -i -e "s/__SW_VERSION__/$(SW_VERSION)/g" \
								  -e "s/__BOARD_NAME__/$(BOARD_NAME)/g" \
								  -e "s/__DATE__/$(shell LC_ALL=C date +"%a, %d %b %Y %T %z")/g" ; \
	fi ; \
	cp -fr $(INSTALL_DIR)/* $(PACKAGE_DIR) ; \
	echo "apres le cp -fr $(INSTALL_DIR)/* $(PACKAGE_DIR)" ; \
	cd $(PACKAGE_DIR) ; \
	pwd; \
	if [ "$(SW_NAME)" = "linux" ] ; then \
		tar cfz ../$(SW_NAME)-kernel-$(BOARD_NAME)_$(SW_VERSION).orig.tar.gz * ; \
	else \
		tar cfz ../$(SW_NAME)-$(BOARD_NAME)_$(SW_VERSION).orig.tar.gz * ; \
	fi ; \
	echo "DEBUILD_ENV :$(DEBUILD_ENV): DEBBUILD :$(DEBUILD): DEBUID_ARGS :$(DEBUILD_ARGS):" ; \
	$(DEBUILD_ENV) $(DEBUILD) $(DEBUILD_ARGS) && $(TARGET_DONE) ; \
	$(TARGET_DONE)

do-repackage:
	@if [ -f $(COOKIE_DIR)/do-package ]  ; then \
		rm -f $(COOKIE_DIR)/do-package ; \
	fi ;
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
#
# Create the Debian package
#

package: install $(PACKAGE_DIR) pre-package do-package post-package
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)


# ------------------------------------------------------------------------------
#
# Execute once again the package target
#

repackage: install pre-repackage do-repackage package post-repackage
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

# Match initial ifdef DFT_TARGET_PACKAGE
endif
