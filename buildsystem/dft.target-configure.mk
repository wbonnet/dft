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
$(info included dft.target-configure.mk)
ifdef DFT_BUILDSYSTEM_TARGET_CONFIGURE
$(error dft.target-configure.mk has already been included)
else
define DFT_BUILDSYSTEM_TARGET_CONFIGURE
endef
# the matching endif teminates this file

# ------------------------------------------------------------------------------
#
# Run the configure script
#

#yavait caCONFIGURE_TARGETS = $(addprefix configure-,$(basedir $(CONFIGURE_SCRIPTS)))
CONFIGURE_TARGETS = $(addprefix configure-, $(CONFIGURE_SCRIPTS))

#configure : patch $(SRC_DIR) pre-configure $(CONFIGURE_TARGETS) $(CONFIGURE_SCRIPTS) do-configure post-configure
configure : patch pre-configure do-configure post-configure
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
#
# Force running again the configure script
#

RECONFIGURE_TARGETS ?= $(addprefix reconfigure-,$(basedir $(CONFIGURE_SCRIPTS)))

reconfigure : patch pre-reconfigure $(RECONFIGURE_TARGETS) configure post-reconfigure
	@rm -f $(COOKIE_DIR)/configure
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
#
# Execute the configure script
#
# TODO : DELTA DEFCONFIG
# ya pas de configure t as deja lz .config			$(CONFIGURE_ENV) $(abspath $*)/configure $(CONFIGURE_ARGS) ; 

%/configure : do-configure 
configure : do-configure 
do-configure :
	@if test -f $(COOKIE_DIR)/$* ; then \
		true ; \
	else \
		if [ "$(SRC_NAME)" = "u-boot" ] ; then \
			echo "    running make $(BUILD_FLAGS) $(UBOOT_DEFCONFIG) in $(SRC_DIR)" ; \
			cd "$(SRC_DIR)/$(SRC_NAME)-$(SW_VERSION)" && make $(BUILD_FLAGS) $(UBOOT_DEFCONFIG) ; \
		else \
			if [ "$(SRC_NAME)" = "linux" ] ; then \
				cd "$(SRC_DIR)/$(SRC_NAME)-$(SW_VERSION)" ; \
				cp "$(DEFCONFIG_DIR)/$(BOARD_NAME)-kernel-$(SW_VERSION).config" .config ; \
				make olddefconfig ; \
				cp .config "$(DEFCONFIG_DIR)/$(BOARD_NAME)-kernel-$(SW_VERSION).config" ; \
			else \
				echo "  UNKNOWN SRC_NAME $(SRC_NAME)" ; \
			fi ; \
		fi ; \
	fi ;
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
# Match initial ifdef
endif

