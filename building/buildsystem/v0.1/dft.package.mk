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
# Copyright 2017 DFT project (http://www.debianfirmwaretoolkit.org).
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
# Execute the package target script
#

do-package :
	@if test -f $(COOKIE_DIR)/do-package ; then \
		true ; \
	else \
		echo "        running package in $(PACKAGE_DIR)"  ; \
		cd $(PACKAGE_DIR) ; \
		mkdir -p linux-kernel-$(BOARD_NAME) ; \
		cd linux-kernel-$(BOARD_NAME) ; \
		rm -f debian ; \
		cp -fr $(BASE_DIR)/debian debian ; \
		cp -fr $(abspath $(INSTALL_DIR))/* . ; \
	 	if [ ! "" = "$(UBOOT_VERSION)" ] ; then \
			tar cvfz ../uboot-$(BOARD_NAME)_$(KERNEL_VERSION).orig.tar.gz * ; \
		else \
			tar cvfz ../linux-kernel-$(BOARD_NAME)_$(KERNEL_VERSION).orig.tar.gz * ; \
	 	fi ; \
		$(DEBUILD_ENV) $(DEBUILD) $(DEBUILD_ARGS) ; \
	fi ;
	@$(TARGET_DONE)

do-repackage :
	@if test -f $(COOKIE_DIR)/do-package ; then \
		rm -f $(COOKIE_DIR)/do-package ; \
		rm -fr $(abspath $(PACAKGE_DIR)) ; \
	fi ;
	$(TARGET_DONE)

