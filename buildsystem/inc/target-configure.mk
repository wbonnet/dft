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
ifdef DFT_BUILDSYSTEM_TARGET_CONFIGURE
$(error target-configure.mk has already been included)
else
define DFT_BUILDSYSTEM_TARGET_CONFIGURE
endef
# the matching endif teminates this file

# ------------------------------------------------------------------------------
#
# Run the configure script
#

CONFIGURE_TARGETS = $(addprefix configure-, $(CONFIGURE_SCRIPTS))

configure: patch pre-configure do-configure post-configure
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
#
# Force running again the configure script
#

RECONFIGURE_TARGETS ?= $(addprefix reconfigure-,$(basedir $(CONFIGURE_SCRIPTS)))

reconfigure: patch pre-reconfigure $(RECONFIGURE_TARGETS) configure post-reconfigure
	@rm -f $(COOKIE_DIR)/configure
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
#
# Execute the configure script
#
# TODO : DELTA DEFCONFIG

configure: extract pre-configure do-configure post-configure 
do-configure:
	@if [ ! "x$(HOST_ARCH)" = "x$(BOARD_ARCH)" ] ; \
	then \
		echo "Makefile processing had to be stopped during target $@ execution. The target board is based on $(BOARD_ARCH) architecture and make is running on a $(HOST_ARCH) board." ; \
		echo "The generated binaries might be invalid or scripts could fail before reaching the end of target. Cross compilation is not yet supported." ; \
		echo "Processing will now continue only for $(HOST_ARCH) based boards package definitions." ; \
		echo "You can get the missing binaries by running again this target on a $(BOARD_ARCH) based host and collect the generated items." ; \
		echo "To generate binaries for all architectures you will need (for now) several builders, one for each target architecture flavor." ; \
	fi ; 
	@if test -f $(COOKIE_DIR)/$@ ; then \
		echo "cookie $(COOKIE_DIR)/$@" ; \
		true ; \
	else \
		cd $(BUILD_DIR)/$(SW_NAME)-$(SW_VERSION) ; \
		pwd ; \
		if [ "$(SW_NAME)" = "u-boot" ] ; then \
			echo "    running u-boot make $(BUILD_FLAGS) $(UBOOT_DEFCONFIG) in $(BUILD_DIR)" ; \
			make $(BUILD_FLAGS) $(UBOOT_DEFCONFIG) ; \
		else \
			if [ "$(SW_NAME)" = "linux" ] ; then \
				cp "$(DEFCONFIG_DIR)/$(BOARD_NAME)-kernel-$(SW_VERSION).config" .config ; \
				pwd ; \
				echo " cp $(DEFCONFIG_DIR)/$(BOARD_NAME)-kernel-$(SW_VERSION).config .config" ; \
				echo "    running kernel make silentoldconfig in `pwd`" ; \
				make silentoldconfig ; \
				cp .config "$(DEFCONFIG_DIR)/$(BOARD_NAME)-kernel-$(SW_VERSION).config" ; \
			fi ; \
		fi ; \
	fi ;
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
# Match initial ifdef
endif

