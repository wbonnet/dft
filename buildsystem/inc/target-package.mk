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
	echo "DEBUG target-package.mk HOST_ARCH __$(HOST_ARCH)__ BOARD_ARCH __$(BOARD_ARCH)__" ; \
	if [ "$(SW_VERSION)" = "" ] ; then \
		echo "DEBUG : SW_VERSION is empty of undefined. Not at a defined version level skipping do-package" ; \
	else \
		if [ ! "x$(HOST_ARCH)" = "x$(BOARD_ARCH)" ] ; then \
			echo "Makefile processing had to be stopped during target $@ execution." ; \
			echo "The target board is based on $(BOARD_ARCH) architecture and make is running on a $(HOST_ARCH) board." ; \
			echo "The generated binaries might be invalid or scripts could fail before reaching the end of target. Cross compilation is not yet supported." ; \
			echo "Processing will now continue only for $(HOST_ARCH) based boards package definitions." ; \
			echo "You can get the missing binaries by running again this target on a $(BOARD_ARCH) based host and collect the generated items." ; \
			echo "To generate binaries for all architectures you will need (for now) several builders, one for each target architecture flavor." ; \
		else \
			if [ ! -f $(COOKIE_DIR)/do-package ] ; then \
				echo "DEBUG je suis dans le PWD :$(PWD)"  ; \
				echo "DEBUG I try to cd $(BUILD_DIR)/$(SW_NAME)-$(SW_VERSION)" ;  \
				echo "ls -l $(PWD)/files"  ; \
				ls -l $(PWD)/files  ; \
				cp -frv --dereference files $(PACKAGE_DIR)/doc ; \
				echo "DEBUG et je vais copier le squelette de paquet dans $(PACKAGE_DIR)" ; \
				if [ "$(SW_NAME)" = "linux" ] ; then \
					cp -fr --dereference $(DFT_BUILDSYSTEM)/templates/debian-kernel-package $(PACKAGE_DIR)/debian ; \
					cp --dereference $(DFT_BUILDSYSTEM)/templates/linux-kernel-version.makefile $(PACKAGE_DIR)/Makefile ; \
				else \
					cp -frv $(DFT_BUILDSYSTEM)/templates/debian-u-boot-package $(PACKAGE_DIR)/debian ; \
					echo "DEBUG contenu de PACKAGE_DIR $(PACKAGE_DIR)" ; \
					tree $(PACKAGE_DIR) ; \
					echo "DEBUG et moi je suis dans" ; \
					pwd ; \
				fi ; \
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
				find $(PACKAGE_DIR)/debian -type f | xargs sed -i -e "s/__SW_VERSION__/$(SW_VERSION)/g" \
										  -e "s/__BOARD_NAME__/$(BOARD_NAME)/g" \
										  -e "s/__DATE__/$(shell LC_ALL=C date +"%a, %d %b %Y %T %z")/g" ; \
				cp -fr $(INSTALL_DIR)/* $(PACKAGE_DIR) ; \
				cd $(PACKAGE_DIR) ; \
				if [ "$(SW_NAME)" = "linux" ] ; then \
					tar cfz ../$(SW_NAME)-kernel-$(BOARD_NAME)_$(SW_VERSION).orig.tar.gz * ; \
				else \
					tar cfz ../$(SW_NAME)-$(BOARD_NAME)_$(SW_VERSION).orig.tar.gz * ; \
				fi ; \
			fi ; \
		fi ; \
		echo "DEBUG : dans le do-package avant le cd PACKAGE_DIR $(PACKAGE_DIR)" ; \
		echo "DEBUG : Je suis dans "; \
		pwd ; \
		cd $(PACKAGE_DIR) ; \
		echo "DEBUG : Juste avant le debuild"; \
		$(DEBUILD_ENV) $(DEBUILD) $(DEBUILD_ARGS) ; \
		echo "DEBUG : Juste apres le debuild"; \
	fi ; \
	echo "DEBUG : fin de do-package juste avant le target-done. Je suis dans :"; \
	pwd;
	$(TARGET_DONE)

do-repackage:
	@if [ -f $(COOKIE_DIR)/do-package ]  ; then 
		rm -f $(COOKIE_DIR)/do-package ; 
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
