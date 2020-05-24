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
ifdef DFT_TARGET_CONFIGURE
$(info target-configure.mk has already been included)
else
#$(info now including target-configure.mk)
DFT_TARGET_CONFIGURE = 1

# Some temporary default values used to debug where where variables are initialized
SW_NAME     ?= out-of-scope
SW_VERSION  ?= out-of-scope

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
	skip_target=0 ; \
# Check if make is running at generic level or target to build level \
	if [ "$(SW_VERSION)" == "out-of-scope" ] ; then \
		skip_target=1 ; \
		true ; \
	fi; \
\
	if [ ! "x$(HOST_ARCH)" = "x$(BOARD_ARCH)" ] && [ "x$(only-native-arch)" = "x1" ] ; then \
		skip_target=1 ; \
		if [ ! "x$(no-arch-warning-arch)" = "x1" ] ; then \
			echo "Makefile processing had to be stopped during target $@ execution. Cross compilation is not supported. " ; \
			echo "The target board is based on $(BOARD_ARCH) architecture and make is running on a $(HOST_ARCH) board." ; \
		  echo "The generated binaries might be invalid or scripts could fail before reaching the end of target." ; \
			echo "Makefile will now continue and process only $(HOST_ARCH) based boards. You can get the missing binaries by running" ; \
			echo "this target again on a $(BOARD_ARCH) based host and collect by yourself the generated items." ; \
			echo "In order to generate binaries for existing architectures, you need several builders, one for each target arch." ; \
		fi ; \
	fi ; \
# Check if target should be executed even if current arch is different from target arch \
# Check if skip flag has been raised it not then do the job \
	if [ ! "x$$skip_target" = "x1" ] ; then \
		if [ -f $(COOKIE_DIR)/$@ ] ; then \
			echo " DEBUG : cookie $(COOKIE_DIR)/$@ already exist, nothing left to do for make do-configure" ; \
		else \
			if [ "$(SW_NAME)" = "u-boot" ] ; then \
# Test if current package is a u-boot then copy template files \
				if [ ! -f "configs/$(UBOOT_DEFCONFIG)" ] ; then \
					echo "ERROR defconfig file $(UBOOT_DEFCONFIG) for board $(BOARD_NAME) does not exist in $(SW_NAME) v$(SW_VERSION) sources." ; \
					$(call dft_error ,2001-1001) ; \
				else \
					cd $(BUILD_DIR) ; \
					echo "    running u-boot make $(BUILD_FLAGS) $(UBOOT_DEFCONFIG) in $(BUILD_DIR)" ; \
					make -C $(BUILD_DIR) $(BUILD_FLAGS) $(UBOOT_DEFCONFIG) ; \
				fi ; \
			else \
# Test if current package is a linux kernel then copy template files \
				if [ "$(SW_NAME)" = "linux" ] ; then \
					if [ ! -f "../config/$(BOARD_NAME)-kernel-$(SW_VERSION).config" ] ; then \
						echo "DEBUG : config/$(BOARD_NAME)-kernel-$(SW_VERSION).config does not exist using default instead" ; \
						cp "config/$(BOARD_NAME)-kernel-default.config" $(BUILD_DIR)/.config ; \
					else \
						echo "DEBUG : config/$(BOARD_NAME)-kernel-$(SW_VERSION).config exist !" ; \
						cp "../config/$(BOARD_NAME)-kernel-$(SW_VERSION).config" $(BUILD_DIR)/.config ; \
					fi ; \
					cd $(BUILD_DIR) ; \
					echo "DEBUG : now running kernel make olddefconfig in `pwd`" ; \
					echo "DEBUG : existing .config files have been backuped up to beforolddefconfig and afterolddefconfig" ; \
					cp .config "$(BOARD_NAME)-kernel-$(SW_VERSION).beforeolddefconfig" ; \
					md5sum "$(BOARD_NAME)-kernel-$(SW_VERSION).beforeolddefconfig" ; \
					make olddefconfig ; \
					cp .config "$(BOARD_NAME)-kernel-$(SW_VERSION).afterolddefconfig" ; \
					md5sum "$(BOARD_NAME)-kernel-$(SW_VERSION).afterolddefconfig" ; \
				fi ; \
			fi ; \
		fi ; \
	fi ;
	$(TARGET_DONE)

# Match initial ifdef DFT_TARGET_CONFIGURE
endif

