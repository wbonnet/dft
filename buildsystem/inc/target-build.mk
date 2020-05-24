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
#$(info now including target-build.mk)
DFT_TARGET_BUILD = 1

# Some temporary default values used to debug where where variables are initialized
SW_NAME     ?= out-of-scope
SW_VERSION  ?= out-of-scope

# ------------------------------------------------------------------------------
#
# Build the target binaries
#

BUILD_TARGETS ?= $(addprefix build-,$(SRC_DIST_FILES))

show-build-targets:
	@echo $(BUILD_TARGETS) ;

build: configure pre-build $(BUILD_TARGETS) post-build
	@skip_target=0 ; \
\
# Check if make is running at generic level or target to build level \
	if [ "$(SW_VERSION)" == "out-of-scope" ] ; then \
		skip_target=1 ; \
		true ; \
  fi ; \
\
	if [ ! "x$(HOST_ARCH)" = "x$(BOARD_ARCH)" ] && [ "x$(only-native-arch)" = "x1" ] ; then \
		skip_target=1 ; \
		if [ "x$(arch-warning)" = "x1" ] ; then \
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
		cd $(BUILD_DIR) ; \
		if [ ! -f $(COOKIE_DIR)/$@ ] ; then \
			$(BUILD_ENV) $(MAKE) $(BUILD_PROCESS_COUNT) $(BUILD_FLAGS) $(BUILD_ARGS) \
                   only-native-arch=$(only-native-arch) arch-warning=$(arch-warning); \
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
	@rm -f $(COOKIE_DIR)/build
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
#
# Execute the building script
#

build-%:
	echo "debug 1 : $$skip_target" ;  \
	skip_target=0 ; \
	echo "debug 2 : $$skip_target" ;  \
\
# Check if make is running at generic level or target to build level
	if [ "$(SW_VERSION)" == "out-of-scope" ] ; then \
		skip_target=1 ; \
		echo "debug 3 : $$skip_target _x_" ;  \
		true ; \
  fi ; \
\
# Check if target should be executed even if current arch is different from target arch
	if [ ! "x$(HOST_ARCH)" = "x$(BOARD_ARCH)" ] && [ "x$(only-native-arch)" = "x1" ] ; then \
		skip_target=1 ; \
		echo "debug 6 : Je force le skip_target" ;  \
		echo "debug 4 : $$skip_target" ;  \
		if [ "x$(arch-warning)" = "x1" ] ; then \
			echo "Makefile processing had to be stopped during target $@ execution. Cross compilation is not supported. " ; \
			echo "The target board is based on $(BOARD_ARCH) architecture and make is running on a $(HOST_ARCH) board." ; \
		  echo "The generated binaries might be invalid or scripts could fail before reaching the end of target." ; \
			echo "Makefile will now continue and process only $(HOST_ARCH) based boards. You can get the missing binaries by running" ; \
			echo "this target again on a $(BOARD_ARCH) based host and collect by yourself the generated items." ; \
			echo "In order to generate binaries for existing architectures, you need several builders, one for each target arch." ; \
		fi ; \
	fi ; \
 # Check if skip flag has been raised it not then do the job \
	if [ ! "x$$skip_target" = "x1" ] ; then \
		echo "debug 5 : x_$$skip_target _x_" ;  \
		cd $(BUILD_DIR) ; \
		pwd ; \
		echo "dans skip_target  != 1 : x $$skip_target _x_" ;  \
		if [ ! -f $(COOKIE_DIR)/build-$* ] ; then \
			$(BUILD_ENV) $(MAKE) $(BUILD_PROCESS_COUNT) $(BUILD_FLAGS) $(BUILD_ARGS) ; \
		fi ; \
	fi ;
	$(DISPLAY_COMPLETED_TARGET_NAME)
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
