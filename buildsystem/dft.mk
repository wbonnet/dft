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

.PHONY: help

# ------------------------------------------------------------------------------
#
# Protection against multiple includes
#
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
# Check if the DFT_HOME has been defined, if not output an error before doing anything.
# DFT_HOME is a shell variable that must target to the path where dft id installed
# DFT_HOME has to contain the buildsystem folder
#
ifeq ($(DFT_HOME), )
define error_msg


DFT_HOME must be defined in the environment of shell running the make command.
Warning ! DFT_HOME must be a relative path, you cannot git add symlinks to an
absolute path. Otherwise, it would not work for environment different from yours.

You have to set DFT_HOME before continuing. It can be done by adding following
line to ~/.bash_aliases and by executing it interactively for current shell.

export DFT_HOME=$(dir $(lastword $(MAKEFILE_LIST)))

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


BOARD_ARCH variable as not yet been defined in the board.mk Makefile.
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

export DEBFULLNAME="Jane Doe"

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

export DEBEMAIL="jane@doe.org"

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
TARGET_DONE = echo "debug cookiemaker : cookiedir = $(COOKIE_DIR)" && mkdir -p $(COOKIE_DIR) && touch $(COOKIE_DIR)/$(notdir $@)

# ------------------------------------------------------------------------------
#
# Determine this Makefile directory which is the root of the build system
#
BUILD_SYSTEM := $(dir $(lastword $(MAKEFILE_LIST)))

# ------------------------------------------------------------------------------
#
# Includes the build system top level and target definitions
#
# ------------------------------------------------------------------------------
include $(BUILD_SYSTEM)/inc/conf.mk
include $(BUILD_SYSTEM)/inc/lib.mk
include $(BUILD_SYSTEM)/inc/target-build.mk
include $(BUILD_SYSTEM)/inc/target-configure.mk
include $(BUILD_SYSTEM)/inc/target-extract.mk
include $(BUILD_SYSTEM)/inc/target-fetch.mk
include $(BUILD_SYSTEM)/inc/target-install.mk
include $(BUILD_SYSTEM)/inc/target-package.mk
include $(BUILD_SYSTEM)/inc/target-upload.mk

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
help:
	@echo "Available targets are :"
	@echo "   clean                   Call the clean target inside the work directory"
	@echo "                           then into all its subfolders (sub makefiles have"
	@echo "                           to support the clean target or an arror will occur)"
	@echo "   mrproper                Destroy the work directory content and remove all"
	@echo "                           cookies. Thus every steps done will have to be executed again"
	@echo "                           since there will be nothing left in work directory."
	@echo "                           Sources will be (re)downloaded then extracted, compiled, etc."
	@echo "                           This may take a lot of time."
	@echo "                           "
	@echo "                           Warning !!! You will loose all the local modifications you may have done !!!"
	@echo "                           You have been warned :)"
	@echo "                           "
	@echo "   show-config(uration)    Display the build system configuration and values of internal variables"
	@echo "   fetch                   Download software sources from upstream site"
	@echo "   fetch-list              Show list of files that would be retrieved by fetch"
	@echo "   checksum                Compare the checksums of downloaded files to the content of checksums file"
	@echo "   makesum(s)              Compute the checksums and create the checksum file"
	@echo "   extract                 Extract the content of the files downloaded by fetch target"
	@echo "   patch                   Apply the patches identified by the PATCHFILES Makefile variable"
	@echo "   configure               Execute the configure script"
	@echo "   build                   Build the software from sources"
	@echo "   install                 Install the software to the target directory under workdir"
	@echo "   package                 Build all versions of BSP software packages (both linux kernel and u-boot)"
	@echo "   u-boot-package          Build all versions of u-boot package (and only u-boot, thus no kernel)"
	@echo "                           for board $(BOARD_NAME)"
	@echo "   kernel-package          Build all versions of linux kernel package (and only linux kernel, thus not of u-boot)"
	@echo "                           for board $(BOARD_NAME)"
	@echo "   sanity-check            Verify the availability of required items (files, symlinks, directories)"
	@echo "   re[target]              Force execution of [target] even if already done (without re-executing dependencies)"
	@echo "                           "
	@echo "                           All targets are recursive. It means that make will walk down through the whole tree."
	@echo "                           Iterating categories, then boards, softwares, every versions and finally call the"
	@echo "                           given target in current location. Recursive target execution is handy but it can"
	@echo "                           use a lot of time, cpu and network bandwidth."
	@echo "                           "
	@echo "                           Please note that during tree walk if host and target architectures are different make"
	@echo "                           will NOT execute configure, install nor build targets. Host is the machine you use to"
	@echo "                           run make command and target is the machine you are building for."
	@echo "                           "
	@echo "                           Since cross compilation is not yet supported, to build binaries for different arch"
	@echo "                           you need at least one builder per arch and collect generated .deb files"

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
show-config:
	@echo "Sources download with $(DOWNLOAD_TOOL) and parameters" ; 
	@echo "  SW_NAME                           $(SW_NAME)" ; 
	@echo "  SW_VERSION                        $(SW_VERSION)" ; 
	@if [ "$(DOWNLOAD_TOOL)" = "wget" ]; then \
		echo "  SRC_DIST_FILES                    $(SRC_DIST_FILES)" ; \
		echo "  SRC_SIGN_FILES                    $(SRC_SIGN_FILES)" ; \
		echo "  SRC_DIST_URL                      $(SRC_DIST_URL)" ; \
	fi ;
	@if [ "$(DOWNLOAD_TOOL)" = "git" ]; then \
		echo "  GIT_URL                           $(GIT_URL)" ; \
		echo "  GIT_REPO                          $(GIT_REPO)" ; \
		echo "  GIT_REPO_EXT                      $(GIT_REPO_EXT)" ; \
		echo "  GIT_BRANCH                        $(GIT_BRANCH)" ; \
	fi ;
	@echo 
	@echo "Directories configuration"
	@echo "  BUILD_SYSTEM                      $(BUILD_SYSTEM)"
	@echo "  DFT_HOME                          $(DFT_HOME)"
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

setup: $(COOKIE_DIR)
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
# Match initial ifdef
endif
