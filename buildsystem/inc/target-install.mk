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
ifdef DFT_TARGET_INSTALL
$(info target-install.mk has already been included)
else
$(info now including target-install.mk)
DFT_TARGET_INSTALL = 1

# Some temporary default values used to debug where where variables are initialized
SW_NAME     ?= no-name-at-target-install
SW_VERSION  ?= no-version-at-target-install

# ------------------------------------------------------------------------------
#
# Install software to the target directory
#

install: build $(INSTALL_DIR) pre-install do-install post-install
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
#
# Execute once again the install target
#

reinstall: build pre-reinstall do-reinstall install post-reinstall
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
#
# Execute the install target script
#

do-install:
	@if [ ! "x$(HOST_ARCH)" = "x$(BOARD_ARCH)" ] ; \
	then \
	    echo "Makefile processing had to be stopped during target $@ execution. The target board is based on $(BOARD_ARCH) architecture and make srunning on a $(HOST_ARCH) board." ; \
	    echo "The generated binaries might be invalid or scripts could fail before reaching the end of target. Cross compilation is not yet supported." ; \
		echo "Processing will now continue only for $(HOST_ARCH) based boards package definitions." ; \
		echo "You can get the missing binaries by running again this target on a $(BOARD_ARCH) based host and collect the generated items." ; \
		echo "To generate binaries for all architectures you will need (for now) several builders, one for each target architecture flavor." ; \
	fi ;
	@if test -f $(COOKIE_DIR)/do-install ; then \
		true ; \
	else \
		cd $(BUILD_DIR)/$(SW_NAME)-$(SW_VERSION) ; \
		if [ "$(SW_NAME)" = "u-boot" ] ; then \
			echo "cp -fr $(BUILD_DIR)/$(SW_NAME)-$(SW_VERSION)/files/* $(INSTALL_DIR)/doc/" ; \
			cp -fr $(BUILD_DIR)/$(SW_NAME)-$(SW_VERSION)/files/* $(INSTALL_DIR)/doc/ ; \
			echo "cp -f $(BUILD_DIR)/$(SW_NAME)-$(SW_VERSION)/$(UBOOT_BINARY_FILE) $(INSTALL_DIR)/u-boot/u-boot-$(BOARD_NAME)-$(SW_VERSION)" ; \
			cp -f $(BUILD_DIR)/$(SW_NAME)-$(SW_VERSION)/$(UBOOT_BINARY_FILE) $(INSTALL_DIR)/u-boot/u-boot-$(BOARD_NAME)-$(SW_VERSION) ; \
			cp -f $(BUILD_DIR)/$(SW_NAME)-$(SW_VERSION)/u-boot.dtb $(INSTALL_DIR)/u-boot/u-boot-$(BOARD_NAME)-$(SW_VERSION).dtb ; \
			echo "cp -f $(BUILD_DIR)/$(SW_NAME)-$(SW_VERSION)/u-boot.dtb $(INSTALL_DIR)/u-boot/u-boot-$(BOARD_NAME)-$(SW_VERSION).dtb" ; \
			ln -sf u-boot-$(BOARD_NAME)-$(SW_VERSION) $(INSTALL_DIR)/u-boot/u-boot-$(BOARD_NAME); \
			echo "ln -sf u-boot-$(BOARD_NAME)-$(SW_VERSION) $(INSTALL_DIR)/u-boot/u-boot-$(BOARD_NAME)"; \
		else \
			if [ "$(SW_NAME)" = "linux" ] ; then \
				echo "DEBUG Dans le else du if u-boot" ; \
				echo "DEBUG Dans le if linux" ; \
				echo "INSTALL_DIR : $(INSTALL_DIR)" ; \
				mkdir -p $(INSTALL_DIR)/boot/dtb ; \
				$(BUILD_ENV) $(MAKE) INSTALL_PATH=$(INSTALL_DIR)/boot $(INSTALL_ARGS) ; \
				$(BUILD_ENV) $(MAKE) INSTALL_MOD_PATH=$(INSTALL_DIR)/ INSTALL_MOD_STRIP=1 modules_install ; \
				cp -fr arch/arm/boot/dts/*.dtb $(INSTALL_DIR)/boot/dtb ; \
	 	 		if [ ! "" = "$(DEFAULT_DTB)" ] ; then \
					echo "DEBUG Je suis dans le if a la con" ; \
					cd $(INSTALL_DIR)/boot ; \
					ln -sf dtb/$(DEFAULT_DTB) default.dtb ; \
				else \
					echo "DEBUG Je suis dans le else a la con" ; \
				fi ; \
			fi ; \
		fi ; \
	fi ;
	@$(TARGET_DONE)

do-reinstall:
	@if test -f $(COOKIE_DIR)/do-install ; then \
		rm -f $(COOKIE_DIR)/do-install ; \
		rm -fr $(INSTALL_DIR) ; \
	fi ;
	$(TARGET_DONE)

# Match initial ifdef DFT_TARGET_INSTALL
endif

