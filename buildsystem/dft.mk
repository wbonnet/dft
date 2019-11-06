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
$(info included dft.mk)
ifdef DFT_BUILDSYSTEM_ENTRY_POINT
$(error dft.mk has already been included)
else
define DFT_BUILDSYSTEM_ENTRY_POINT
endef
# the matching endif teminates this file

# ------------------------------------------------------------------------------
#
# Safety check, we need GNU make >= 3.81 for the magic further below,
# more precisly: 3.80 for $(MAKEFILE_LIST), 3.81 for $(lastword ...)
# c.f.: http://cvs.savannah.gnu.org/viewvc/make/NEWS?root=make&view=markup
#
ifeq (,$(and $(MAKEFILE_LIST),$(lastword test)))
define error_msg
GNU make >= 3.81 required.
endef
  $(error $(error_msg))
endif

# ------------------------------------------------------------------------------
#
# Check if the board arch is defined, if not output an error before doing anything.
# It means this bard has been newly created and arch has to be defined
#
ifeq ($(BOARD_ARCH), unknown)
define error_msg


BOARD_ARCH variable as not yet been defined in the $(BOARD_NAME).mk Makefile.
Please replace "unknown" by the board architecture (armv7l, x86_64, ppc64, etc.).


endef
  $(error $(error_msg))
endif


# ------------------------------------------------------------------------------
#
# Check if the DEBFULLNAME is defined. Otherwise package template will not be
# instanciated properly.
#
ifeq ($(DEBFULLNAME), )
define error_msg


DEBFULLNAME environment variable should be defined. You have to set it before
continuing. This can be done by adding the following line to ~/.bash_aliases

export DEBFULLNAME "Jane Doe"

endef
  $(error $(error_msg))
  $(error $(DEBFULLNAME))
endif


# ------------------------------------------------------------------------------
#
# Check if the DEBEMAIL is defined. Otherwise package template will not be
# instanciated properly.
#
ifeq ($(DEBEMAIL), )
define error_msg


DEBEMAIL environment variable shoould be defined. You have to set it before
continuing. This can be done by adding the following line to ~/.bash_aliases

export DEBEMAIL "jane@doe.org"

endef
  $(error $(error_msg))
endif


# ------------------------------------------------------------------------------
#
# Used for output...
#
DISPLAY_TARGET_NOT_IMPLEMENTED = @echo "Target [$@] is not implemented !"
DISPLAY_COMPLETED_TARGET_NAME  = @echo "    completed [$@] "

# ------------------------------------------------------------------------------
#
# Cookie maker
#
TARGET_DONE = @mkdir -p $(COOKIE_DIR) && touch $(COOKIE_DIR)/$(notdir $@)

# ------------------------------------------------------------------------------
#
# Determine this Makefile directory which is the root of the build system
#
BUILD_SYSTEM_ROOT := $(dir $(lastword $(MAKEFILE_LIST)))

# ------------------------------------------------------------------------------
#
# Includes the build system top level and target definitions
#
# ------------------------------------------------------------------------------
include $(BUILD_SYSTEM_ROOT)/dft.internals-conf.mk
include $(BUILD_SYSTEM_ROOT)/dft.internals-lib.mk
include $(BUILD_SYSTEM_ROOT)/dft.target-build.mk
include $(BUILD_SYSTEM_ROOT)/dft.target-configure.mk
include $(BUILD_SYSTEM_ROOT)/dft.target-extract.mk
include $(BUILD_SYSTEM_ROOT)/dft.target-fetch.mk
include $(BUILD_SYSTEM_ROOT)/dft.target-install.mk
include $(BUILD_SYSTEM_ROOT)/dft.target-package.mk
include $(BUILD_SYSTEM_ROOT)/dft.target-upload.mk

# ------------------------------------------------------------------------------
#
# Defines stub targets so that it is possible to define pre-something or
# post-something targets in Makefile. These pre/post will be automagically by
# targets even if not define thanks to stubs
#
# In addition a pre-everything target can be define and is run before the actual
# target
#

# ------------------------------------------------------------------------------
#
# Remove existing task cookie when entering the generic pre-redo task target
#
pre-re%:
	@rm -rf $(COOKIE_DIR)/$*
	@true

pre-%:
	@true

post-%:
	@true


# ------------------------------------------------------------------------------
#
# Target that prints the help
#
help :
	@echo "Available targets are :"
	@echo "   clean                   Call the clean target inside the  work directory"
	@echo "                           then into all its subfolders (sub makefiles have"
	@echo "                           to support the clean target or an arror will occur)"
	@echo "   mrproper                Destroy the work directory content and remove all"
	@echo "                           cookies. Thus every steps will be done once again "
	@echo "                           since there will be nothing left in work directory."
	@echo "                           Sources will be downloaded once again then extracted"
	@echo "                           compiled, etc. This may take a lot of time."
	@echo "                           Warning !!! You will loose all the local "
	@echo "                           modifications you may have done !!!"
	@echo "                           You have been warned :)"
	@echo "   show-config(uration)    Echo the main configuration variable"
	@echo "   fetch                   Download software sources from upstream site"
	@echo "   fetch-list              Show list of files that would be retrieved by fetch"
	@echo "   checksum                Verify the checksums"
	@echo "   makesum(s)              Compute the checksums and create the checksum file"
	@echo "   extract                 Extract the contents of the files download by fetch target"
	@echo "   patch                   Apply the patchs listed in PATCHFILES"
	@echo "   configure               Execute the configure script"
	@echo "   build                   Build the software"
	@echo "   install                 Install the software to the target directory"
	@echo "   package                 Build the Debian package containing kernel or u-boot and all the related files"
	@echo
	@echo "   re[target]              Force execution of [target] even if already done (without execution of its depends)"

# ------------------------------------------------------------------------------
#
# Run the clean target only inside the work directory
#
clean:
	@if [ -d $(WORK_DIR) ] ; then make -C $(WORK_DIR) clean ; fi
	$(DISPLAY_COMPLETED_TARGET_NAME)


# ------------------------------------------------------------------------------
#
# Delete everthing from the work, cookies and download directories
#
mrproper:
	@rm -rf $(WORK_DIR)/*
	$(DISPLAY_COMPLETED_TARGET_NAME)


# ------------------------------------------------------------------------------
#
# Dump the values of the internal variables
#
show-configuration : show-config
show-config :
	@echo "Sources download with $(DOWNLOAD_TOOL) and parameters" ; \
	echo "  SRC_NAME                          $(SRC_NAME)" ; \
	echo "  SW_VERSION                        $(SW_VERSION)" ; \
# la c bon	@if [ "$(DOWNLOAD_TOOL)" = "wget" ]; then echo "ya wget" ; else echo "ya pas wget mais $(DOWNLOAD_TOOL)" ; fi
	@if [ "$(DOWNLOAD_TOOL)" = "wget" ]; then \
	echo "  SRC_DIST_FILES                    $(SRC_DIST_FILES)" ; \
	echo "  SRC_SIGN_FILES                    $(SRC_SIGN_FILES)" ; \
	echo "  SRC_DIST_URL                      $(SRC_DIST_URL)" ; \
       	fi
	@if [ "$(DOWNLOAD_TOOL)" = "git" ]; then \
	echo "  GIT_URL                           $(GIT_URL)" ; \
	echo "  GIT_REPO                          $(GIT_REPO)" ; \
	echo "  GIT_REPO_EXT                      $(GIT_REPO_EXT)" ; \
	echo "  GIT_BRANCH                        $(GIT_BRANCH)" ; \
       	fi
	@echo
	@echo "Directories configuration"
	@echo "  BUILD_SYSTEM_ROOT                 $(BUILD_SYSTEM_ROOT)"
	@echo "  BASE_DIR                          $(BASE_DIR)"
	@echo "  WORK_DIR                          $(WORK_DIR)"
	@echo "  FILE_DIR                          $(FILE_DIR)"
	@echo "  DEFCONFIG_DIR                     $(DEFCONFIG_DIR)"
	@echo "  PATCH_DIR                         $(PATCH_DIR)"
	@echo "  DOWNLOAD_DIR                      $(DOWNLOAD_DIR)"
	@echo "  PARTIAL_DIR                       $(PARTIAL_DIR)"
	@echo "  COOKIE_DIR                        $(COOKIE_DIR)"
	@echo "  SRC_DIR                           $(SRC_DIR)"
	@echo "  INSTALL_DIR                       $(INSTALL_DIR)"
	@echo "  PACKAGE_DIR                       $(PACKAGE_DIR)"
	@echo "  TEMP_DIR                          $(TEMP_DIR)"
	@echo "  LOG_DIR                           $(LOG_DIR)"
	@echo "  CHECKSUM_FILE                     $(CHECKSUM_FILE)"
	@echo
	@echo "Build environnement"
	@echo "  BUILDER_ARCH                      $(BUILDER_ARCH)"
	@echo "  BUILDER_HOSTNAME                  $(BUILDER_HOSTNAME)"
	@echo "  BUILDER_OPERATING_SYSTEM          $(BUILDER_OPERATING_SYSTEM)"
	@echo "  BUILDER_OPERATING_SYSTEM_FLAVOR   $(BUILDER_OPERATING_SYSTEM_FLAVOR)"
	@echo "  BUILDER_OPERATING_SYSTEM_VERSION  $(BUILDER_OPERATING_SYSTEM_VERSION)"
	@echo
	@echo "  CONFIGURE_SCRIPTS                 $(CONFIGURE_SCRIPTS)"
	@echo "  BUILD_SCRIPTS                     $(BUILD_SCRIPTS)"
	@echo
	@echo "  BOARD_NAME                        $(BOARD_NAME)"
	@echo "  BOARD_ARCH                        $(BOARD_ARCH)"
	@echo "  KERNEL_DEFCONFIG                  $(KERNEL_DEFCONFIG)"
	@echo "  UBOOT_DEFCONFIG                   $(UBOOT_DEFCONFIG)"
	@echo
	@echo "  BUILD_FLAGS                       $(BUILD_FLAGS)"
	@echo "  BUILD_ARGS                        $(BUILD_ARGS)"
	@echo "  BUILD_ENV                         $(BUILD_ENV)"
	@echo "  BUILD_PROCESS_COUNT               $(BUILD_PROCESS_COUNT)"
	@echo
	@echo "  MAKE                              $(MAKE)"
	@echo "  DEBUILD                           $(DEBUILD)"
	@echo "  DEBUILD_ARGS                      $(DEBUILD_ARGS)"
	@echo "  DEBUILD_ENV                       $(DEBUILD_ENV)"
	@echo
	@echo "Internal variables"
	@echo "  MAKE_FILTERS                      $(MAKE_FILTERS)"

# ------------------------------------------------------------------------------
#
# Setup target. Currently does nothing, should check for basic building
# packages to be avaiable. Should add a check based on the flavor.
#

setup : $(COOKIE_DIR)
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)


# ------------------------------------------------------------------------------
#
# Mandatory defines that have to be defined at least in the main Makefile
#

ifndef SRC_NAME
$(error bsroot $(BUILD_SYSTEM_ROOT))
$(error SRC_NAME is not set)
endif

ifndef DOWNLOAD_TOOL
$(error DOWNLOAD_TOOL is not set)
endif

# ------------------------------------------------------------------------------
# Match initial ifdef
endif
