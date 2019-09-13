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
# Protection against multiple includes
#
$(info included dft.target-install.mk)
ifdef DFT_BUILDSYSTEM_TARGET_INSTALL
$(error dft.target-install.mk has already been included)
else
define DFT_BUILDSYSTEM_TARGET_INSTALL
endef
# the matching endif teminates this file

# ------------------------------------------------------------------------------
#
# Execute the install target script
#

do-install :
	@if test -f $(COOKIE_DIR)/do-install ; then \
		true ; \
	else \
		echo "        running install in $(OBJ_DIR)"  ; \
	 	if [ ! "" = "$(UBOOT_VERSION)" ] ; then \
			mkdir -p $(abspath $(INSTALL_DIR))/u-boot/ ; \
			mkdir -p $(INSTALL_DIR)/doc ; \
			cp files/* $(INSTALL_DIR)/doc ; \
			cd $(abspath $(OBJ_DIR)) ; \
			cp -fr $(UBOOT_BINARY_FILE) $(abspath $(INSTALL_DIR))/u-boot/u-boot-$(BOARD_NAME)-$(UBOOT_VERSION) ; \
			cp -fr u-boot.dtb $(abspath $(INSTALL_DIR))/u-boot/u-boot-$(BOARD_NAME)-$(UBOOT_VERSION).dtb ; \
			cd $(abspath $(INSTALL_DIR))/u-boot/ ; \
			ln -sf u-boot-$(BOARD_NAME)-$(UBOOT_VERSION) u-boot-$(BOARD_NAME); \
	 	else \
			echo "        running install in $(OBJ_DIR)"  ; \
			mkdir -p $(abspath $(INSTALL_DIR))/boot/dtb ; \
			cd $(abspath $(OBJ_DIR)) ; \
			$(BUILD_ENV) $(MAKE) INSTALL_PATH=$(abspath $(INSTALL_DIR))/boot $(INSTALL_ARGS) ; \
			$(BUILD_ENV) $(MAKE) INSTALL_MOD_PATH=$(abspath $(INSTALL_DIR))/ INSTALL_MOD_STRIP=1 modules_install ; \
			cp -fr arch/arm/boot/dts/*.dtb $(abspath $(INSTALL_DIR))/boot/dtb ; \
	 	    if [ ! "" = "$(DEFAULT_DTB)" ] ; then \
			    cd $(abspath $(INSTALL_DIR)/boot) ; \
			    ln -sf dtb/$(DEFAULT_DTB) default.dtb ; \
		    fi ; \
		fi ; \
	fi ;
	@$(TARGET_DONE)

do-reinstall :
	@if test -f $(COOKIE_DIR)/do-install ; then \
		rm -f $(COOKIE_DIR)/do-install ; \
		rm -fr $(abspath $(INSTALL_DIR)) ; \
	fi ;
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
# Match initial ifdef
endif

