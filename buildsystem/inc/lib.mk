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
ifdef DFT_LIB
$(info lib.mk has already been included)
else
$(info now including lib.mk)
DFT_LIB = 1
# Some temporary default values used to debug where where variables are initialized

# ------------------------------------------------------------------------------
#
# Directory maker used by the base rules
#
#$(sort $(DFT_WORKSPACE) $(FILE_DIR) $(GIT_DIR) $(WORK_DIR) $(PARTIAL_DIR) $(COOKIE_DIR) $(INSTALL_DIR) $(PACKAGE_DIR) $(DEFCONFIG_DIR) $(LOG_DIR) $(DOWNLOAD_DIR) $(PATCH_DIR) $(BUILD_DIR))/%:

$(DOWNLOAD_DIR): $(WORK_DIR)
	@if ! test -d $(DOWNLOAD_DIR) ; then \
		echo "DOWNLOAD_DIR does not exist yet, let's create directory $(DOWNLOAD_DIR)"; \
		mkdir -p $(DOWNLOAD_DIR); \
	fi ;

$(DFT_WORKSPACE): $(TEMP_DIR)
	if ! test -d $@ ; then \
		echo "$@ does not exist yet, let's create the missing directory"; \
		mkdir -p $@; \
	fi ;

$(COOKIE_DIR):
	@if ! test -d $(COOKIE_DIR) ; then \
		echo "COOKIE_DIR does not exist yet, let's create directory $(COOKIE_DIR)"; \
		mkdir -p $(COOKIE_DIR); \
	fi ;

$(BUILD_DIR): $(WORK_DIR)
	@if ! test -d $(BUILD_DIR) ; then \
		echo "BUILD_DIR does not exist yet, let's create directory $(BUILD_DIR)"; \
		mkdir -p $(BUILD_DIR); \
	fi ;

$(INSTALL_DIR): $(WORK_DIR)
	@if ! test -d $(INSTALL_DIR) ; then \
		echo "INSTALL_DIR does not exist yet, let's create directory $(INSTALL_DIR)"; \
		mkdir -p $(INSTALL_DIR); \
	fi ;

$(PACKAGE_DIR): $(WORK_DIR)
	@if ! test -d $(PACKAGE_DIR) ; then \
		echo "PACKAGE_DIR does not exist yet, let's create directory $(PACKAGE_DIR)"; \
		mkdir -p $(PACKAGE_DIR); \
	fi ;

$(WORK_DIR):
	@if ! test -d $(WORK_DIR) ; then \
		echo "WORK_DIR does not exist yet, let's create directory $(WORK_DIR)"; \
		mkdir -p $(WORK_DIR); \
	fi ;


# ------------------------------------------------------------------------------
#
# definition of function dft_error : display an error code stop
# execution returning with provided error code or 1 as default value
# TODO Handle default error code
define dft_error =
echo "DFT ERROR CODE : $(1)" && exit 1
endef

define dft_error_message =
echo "DFT ERROR MSG : $(1)" 
endef

# ------------------------------------------------------------------------------
#
# definition of function dft_warning : display a message and continue execution
#
define dft_warning = 
@echo "DFT Warning : $(1)" ;
endef

# Match initial ifdef DFT_LIB
endif
