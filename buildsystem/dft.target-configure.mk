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

CONFIGURE_TARGETS ?= $(addprefix configure-,$(CONFIGURE_SCRIPTS))

configure : patch $(SRC_DIR) pre-configure $(CONFIGURE_TARGETS) post-configure
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)


# ------------------------------------------------------------------------------
#
# Force running again the configure script
#

RECONFIGURE_TARGETS ?= $(addprefix reconfigure-,$(CONFIGURE_SCRIPTS))

reconfigure : patch pre-reconfigure $(RECONFIGURE_TARGETS) configure post-reconfigure
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
#
# Execute the configure script
#
# TODO : DELTA DEFCONFIG
configure-%/configure :
	if test -f $(COOKIE_DIR)/configure-$*/configure ; then \
		true ; \
	else \
		if [ "$(SRC_NAME)" = "u-boot" ] ; then \
			if [ "$(UBOOT_DEFCONFIG)" != "" ] ; then \
				echo "   DEBUG W no dotconfig to copy for u-boot it is generated" ; \
				echo "    running make $(BUILD_FLAGS) $(UBOOT_DEFCONFIG) in $(SRC_DIR)" ; \
				cd "$(SRC_DIR)" && make $(UBOOT_DEFCONFIG); \
			fi ; \
		else \
			if [ "$(SRC_NAME)" = "linux" ] ; then \
				echo "   DEBUG W kernel -> copying $(FILE_DIR)/configs/$(KERNEL_DEFCONFIG) to .config" ; \
				cd "$(SRC_DIR)" && make olddefconfig ; \
				cp .config after_olddefconfig-$(SW_VERSION) ; \
				echo "    running configure in $(SRC_DIR)" ; \
				cd "$(SRC_DIR)" && $(CONFIGURE_ENV) $(abspath $*)/configure $(CONFIGURE_ARGS) ; \
				echo "    DEBUG W plop configure in $(SRC_DIR)" ; \
			fi ; \
		fi ; \
	fi ;
	$(TARGET_DONE)

reconfigure-%/configure :
	@if test -f $(COOKIE_DIR)/configure-$*/configure ; then \
		rm -f $(COOKIE_DIR)/configure-$*/configure ; \
	fi ;
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
# Match initial ifdef
endif

