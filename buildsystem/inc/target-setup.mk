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
ifdef DFT_TARGET_SETUP
$(info target-setup.mk has already been included)
else
DFT_TARGET_SETUP = 1

# ------------------------------------------------------------------------------
#
# Setup target. Currently does nothing, should check for basic building
# packages to be avaiable. Should add a check based on the flavor.
#

setup:
	@mkdir -p $(DFT_WORKSPACE)
	@if [ ! "$(SW_VERSION)" = "" ] ; then \
		mkdir -p $(WORK_DIR) ; \
		mkdir -p $(COOKIE_DIR) ; \
		mkdir -p $(INSTALL_DIR) ; \
		mkdir -p $(PACKAGE_DIR) ; \
		mkdir -p $(DOWNLOAD_DIR) ; \
		mkdir -p $(BUILD_DIR) ; \
		mkdir -p $(LOG_DIR) ; \
		if [ "$(DOWNLOAD_TOOL)" = "wget" ] ; then \
			mkdir -p $(PARTIAL_DIR) ; \
		fi ; \
		if [ "$(DOWNLOAD_TOOL)" = "wget" ] ; then \
			mkdir -p $(GIT_DIR) ; \
		fi ; \
	fi
	@mkdir -p $(FILE_DIR)
	@mkdir -p $(DEFCONFIG_DIR)
	@mkdir -p $(PATCH_DIR)
	@for v in $(filter-out $(MAKE_FILTERS),$(shell find .  -mindepth 1 -maxdepth 1 -type d -printf '%P\n')) ; do \
		$(MAKE) --no-print-directory -C --directory=$$v $@ only-native-arch=$(only-native-arch) arch-warning=$(arch-warning); \
	done ; 
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

# Match initial ifdef DFT_TARGET_SETUP
endif
