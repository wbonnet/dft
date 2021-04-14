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
DFT_TARGET_INSTALL = 1

# ------------------------------------------------------------------------------
#
# Install software to the target directory
#

install: build pre-install do-install post-install
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
#
# Execute once again the install target
#

reinstall: build pre-reinstall do-reinstall install post-reinstall
	@rm -f $(COOKIE_DIR)/install
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
#
# Execute the install target script
#

do-install:
	if [ "$(SW_VERSION)" == "undefined-sw-version" ] ; then \
		true ; \
	else \
		if [ ! "x$(HOST_ARCH)" = "x$(BOARD_ARCH)" ] ; then \
			if [ ! "x$(arch-warning)" = "x1" ] ; then \
				if [ ! "x$(only-native-arch)" = "x1" ] ; then \
					echo "Makefile processing had to be stopped during target $@ execution. Cross compilation is not supported. " ; \
					echo "The target board is based on $(BOARD_ARCH) architecture and make is running on a $(HOST_ARCH) board." ; \
				        echo "The generated binaries might be invalid or scripts could fail before reaching the end of target." ; \
					echo "Makefile will now continue and process only $(HOST_ARCH) based boards. You can get the missing binaries by running" ; \
					echo "this target again on a $(BOARD_ARCH) based host and collect by yourself the generated items." ; \
					echo "In order to generate binaries for existing architectures, you need several builders, one for each target arch." ; \
				fi ; \
			fi ; \
		else \
			if [ ! -f $(COOKIE_DIR)/$@ ] ; then \
				if [ "$(SW_NAME)" = "u-boot" ] ; then \
					cp -frv ../files $(INSTALL_DIR)/doc ; \
					mkdir -p $(INSTALL_DIR)/u-boot/ ; \
                                        cp -fv $(BUILD_DIR)/$(UBOOT_BINARY_FILE) $(INSTALL_DIR)/u-boot/u-boot-$(BOARD_NAME)-$(SW_VERSION) ; \
					if [ ! "$(UBOOT_BINARY_EXTRA_FILES)" = "" ] ; then \
					 	echo "to process : $(UBOOT_BINARY_EXTRA_FILES)";  \
						for f in $(UBOOT_BINARY_EXTRA_FILES) ; do \
							echo "copying: _$$f_" ; \
							cp -fv $(BUILD_DIR)/$$f $(INSTALL_DIR)/u-boot/ ; \
						done ; \
					else \
						echo "UBOOT_BINARY_EXTRA_FILES not defined or empty : $(UBOOT_BINARY_EXTRA_FILES)" ;  \
					fi ; \
					cp -fv $(BUILD_DIR)/u-boot.dtb $(INSTALL_DIR)/u-boot/u-boot-$(BOARD_NAME)-$(SW_VERSION).dtb ; \
                                        ln -sf u-boot-$(BOARD_NAME)-$(SW_VERSION) $(INSTALL_DIR)/u-boot/u-boot-$(BOARD_NAME); \
				else \
					if [ "$(SW_NAME)" = "linux" ] ; then \
						cd $(BUILD_DIR) ; \
						mkdir -p $(INSTALL_DIR)/boot/dtb ; \
						$(BUILD_ENV) $(MAKE) INSTALL_PATH=$(INSTALL_DIR)/boot $(INSTALL_ARGS) ; \
						$(BUILD_ENV) $(MAKE) INSTALL_MOD_PATH=$(INSTALL_DIR)/ INSTALL_MOD_STRIP=1 $(ARCH_COMMON_INSTALL_ARGS) ; \
						cp -fr arch/arm/boot/dts/*.dtb $(INSTALL_DIR)/boot/dtb ; \
						echo "DEBUG : le DEFAULT_DTB $(DEFAULT_DTB)" ; \
			 	 		if [ ! "" = "$(DEFAULT_DTB)" ] ; then \
							cd $(INSTALL_DIR)/boot ; \
							ln -sf dtb/$(DEFAULT_DTB) $(INSTALL_DIR)/boot/default.dtb ; \
						else \
							cp -fr arch/arm/boot/dts/*.dtb $(INSTALL_DIR)/boot/dtb ; \
						fi ; \
					fi ; \
				fi ; \
			fi ; \
		fi ; \
	fi ;
	$(TARGET_DONE)

do-reinstall:
	@if [ -f $(COOKIE_DIR)/do-install ] ; then \
		rm -f $(COOKIE_DIR)/do-install ; \
		rm -fr $(INSTALL_DIR) ; \
	fi ;
	$(TARGET_DONE)

# Match initial ifdef DFT_TARGET_INSTALL
endif

