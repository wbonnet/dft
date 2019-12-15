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
# Protection against multiple includes
#
ifdef DFT_BUILDSYSTEM_TARGET_PACKAGE
$(error target-package.mk has already been included)
else
define DFT_BUILDSYSTEM_TARGET_PACKAGE
endef
# the matching endif teminates this file

# ------------------------------------------------------------------------------
#
# Execute the package target script
#

do-package:
	@if [ ! "x$(HOST_ARCH)" = "x$(BOARD_ARCH)" ] ; \
	then \
	    echo "Makefile processing had to be stopped during target $@ execution. The target board is based on $(BOARD_ARCH) architecture and make ris running on a $(HOST_ARCH) board." ; \
	    echo "The generated binaries might be invalid or scripts could fail before reaching the end of target. Cross compilation is not yet supported." ; \
		echo "Processing will now continue only for $(HOST_ARCH) based boards package definitions." ; \
		echo "You can get the missing binaries by running again this target on a $(BOARD_ARCH) based host and collect the generated items." ; \
		echo "To generate binaries for all architectures you will need (for now) several builders, one for each target architecture flavor." ; \
	fi ; 
	if test -f $(COOKIE_DIR)/do-package ; then \
		true ; \
	else \
		pwd ; \
		echo "        before copying stuff to $(PACKAGE_DIR)"  ; \
		if [ "$(SW_NAME)" = "linux" ] ; then \
			cp -fr $(DFT_BUILDSYSTEM)/templates/debian-kernel-package $(PACKAGE_DIR)/debian ; \
			cp $(DFT_BUILDSYSTEM)/templates/templates/linux-kernel-version.makefile $(PACKAGE_DIR)/Makefile ; \
		else \
			cp -fr $(DFT_BUILDSYSTEM)/templates/debian-u-boot-package $(PACKAGE_DIR)/debian ; \
			cp $(DFT_BUILDSYSTEM)/templates/templates/u-boot-version.makefile $(PACKAGE_DIR)/Makefile ; \
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
		sed -i -e "s/__SW_VERSION__/$(NEW_VERSION)/g" $(PACKAGE_DIR)/Makefile ; \
		find $(PACKAGE_DIR)/debian -type f | xargs sed -i -e "s/__SW_VERSION__/$(NEW_VERSION)/g" \
								  -e "s/__BOARD_NAME__/$(BOARD_NAME)/g" \
								  -e "s/__DATE__/$(shell LC_ALL=C date +"%a, %d %b %Y %T %z")/g" ; \
	fi ; \
	cp -fr $(INSTALL_DIR)/* . ; \
	if [ "$(SW_NAME)" = "linux" ] ; then \
		tar cvfz ../$(SW_NAME)-kernel-$(BOARD_NAME)_$(SW_VERSION).orig.tar.gz * ; \
	else \
		tar cvfz ../$(SW_NAME)-$(BOARD_NAME)_$(SW_VERSION).orig.tar.gz * ; \
		pwd ; \
		$(DEBUILD_ENV) $(DEBUILD) $(DEBUILD_ARGS) ; \
	fi ; \
	$(TARGET_DONE)

do-repackage:
	@if test -f $(COOKIE_DIR)/do-package ; then \
		rm -f $(COOKIE_DIR)/do-package ; \
		rm -fr $(abspath $(PACAKGE_DIR)) ; \
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

# ------------------------------------------------------------------------------
# Match initial ifdef
endif

