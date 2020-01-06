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
ifdef DFT_TARGET_BUILD
$(info target-build.mk has already been included)
else
$(info now including target-build.mk)
DFT_TARGET_BUILD = 1

# Some temporary default values used to debug where where variables are initialized
SW_NAME     ?= no-name-at-target-build
SW_VERSION  ?= no-version-at-target-build

# ------------------------------------------------------------------------------
#
# Build the target binaries
#

BUILD_TARGETS ?= $(addprefix build-,$(SRC_DIST_FILES))

show-build-targets:
	@echo $(BUILD_TARGETS) ;

build: configure pre-build $(BUILD_TARGETS) post-build
	if [ "$(SW_VERSION)" = "" ] ; then \
		echo "DEBUG : SW_VERSION is empty of undefined. Not at a defined version level skipping build. Make was running in the path below :" ; \
		pwd ; \
	else  \
		if [ ! "x$(HOST_ARCH)" = "x$(BOARD_ARCH)" ] ; then \
			echo "Makefile processing had to be stopped during target $@ execution. The target board is based on $(BOARD_ARCH) architecture and make is running on a $(HOST_ARCH) board." ; \
			echo "The generated binaries might be invalid or scripts could fail before reaching the end of target. Cross compilation is not yet supported." ; \
			echo "Processing will now continue only for $(HOST_ARCH) based boards package definitions." ; \
			echo "You can get the missing binaries by running this target again on a $(BOARD_ARCH) based host and collect the generated items." ; \
			echo "To generate binaries for all architectures you will need (for now) several builders, one for each target architecture flavor." ; \
		else \
			if [ ! -f $(COOKIE_DIR)/build-v$(SW_VERSION) ] ; then \
				echo "DEBUG : le cookie $(COOKIE_DIR)/build existe pas. Make was running in the path below :" ; \
				pwd ; \
				echo "DEBUG : maintenant je lance le make suivant" ; \
				echo "DEBUG : $(BUILD_ENV) $(MAKE) -C $(BUILD_DIR) $(BUILD_PROCESS_COUNT) $(BUILD_FLAGS) $(BUILD_ARGS)" ; \
				$(BUILD_ENV) $(MAKE) -C $(BUILD_DIR) $(BUILD_PROCESS_COUNT) $(BUILD_FLAGS) $(BUILD_ARGS) ; \
			fi ; \
		fi ; \
	fi ; 
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
#
# Rebuild the target binaries
#

REBUILD_TARGETS ?= $(addprefix rebuild-,$(BUILD_TARGETS))

rebuild: configure pre-rebuild $(REBUILD_TARGETS) build post-rebuild
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
#
# Execute the building script
#

build-%:
	@if [ "$(SW_VERSION)" = "" ] ; then \
		echo "DEBUG : SW_VERSION is empty or undefined. Not at a defined version level skipping build" ; \
	else \
		cd $(BUILD_DIR) ; \
		if [ ! -f $(COOKIE_DIR)/build-$* ] ; then \
			echo "DEBUG : Avant le MAKE" ; \
			$(BUILD_ENV) $(MAKE) $(BUILD_PROCESS_COUNT) $(BUILD_FLAGS) $(BUILD_ARGS) ; \
			echo "DEBUG : Apres le MAKE" ; \
		fi ; \
	fi ; \
	echo "DEBUG : Apres le if version juste avant le target done" ; 
	$(TARGET_DONE)

rebuild-%:
	@if [ -f $(COOKIE_DIR)/build-$* ] ; then \
		rm -f $(COOKIE_DIR)/build-$* ; \
	fi ;
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
#
# Definition of the package that must be installed on each build platform
#

PREREQUISITE_BASE_PKGS ?= make
PREREQUISITE_BASE_PKGS_UBUNTU ?= build-essential
PREREQUISITE_BASE_PKGS_DEBIAN ?= build-essential

# Match initial ifdef DFT_TARGET_BUILD
endif
