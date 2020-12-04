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

# Force bash use instead of sh which is a symlink to dash on Debian. Dash use
# a slightly different syntax for some operators. This way it a known shell.
SHELL := bash

# build system sould be available under board folder as a symlink. Keep it
# locally available under board folder computing a relative path is a nightmare
# and does not work in all cases. Environment variables are not git friendly
# since git add will loose variable name and generate an absolute path, which
# is not comptible with user need ans or workspace relocation nor packagng needs.
# better solutions wille be really welcomeds contributions.

# ------------------------------------------------------------------------------
#
# Protection against multiple include
#
ifdef DFT_BUILDSYSTEM_ENTRY_POINT
$(info dft.mk has already been included)
else
DFT_BUILDSYSTEM_ENTRY_POINT = 1

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


BOARD_ARCH variable as not yet been defined in the board.mk Makefile.
Please replace "unknown" by the board architecture (armv7l, aarch64, mips, x86_64, ppc64, etc.).

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
# The cookie monster^Wmaker
#
# Change only access time not modification
#
TARGET_DONE = mkdir -p "$(COOKIE_DIR)" && touch -a "$(COOKIE_DIR)/$(notdir $@)"

# ------------------------------------------------------------------------------
#
# Retrieve the directory where this Makefile is stored, its the build system root
#
DFT_BUILDSYSTEM := buildsystem

# ------------------------------------------------------------------------------
#
# Includes the build system top level and target definitions
#
# ------------------------------------------------------------------------------
include $(DFT_BUILDSYSTEM)/inc/conf.mk
include $(DFT_BUILDSYSTEM)/inc/lib.mk
include $(DFT_BUILDSYSTEM)/inc/target-build.mk
include $(DFT_BUILDSYSTEM)/inc/target-configure.mk
include $(DFT_BUILDSYSTEM)/inc/target-extract.mk
include $(DFT_BUILDSYSTEM)/inc/target-fetch.mk
include $(DFT_BUILDSYSTEM)/inc/target-install.mk
include $(DFT_BUILDSYSTEM)/inc/target-package.mk
include $(DFT_BUILDSYSTEM)/inc/target-setup.mk
include $(DFT_BUILDSYSTEM)/inc/target-upload.mk
include $(DFT_BUILDSYSTEM)/inc/target-help.mk

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
	@rm -f $(COOKIE_DIR)/$*
	@true

pre-%:
	@true

post-%:
	@true


# ------------------------------------------------------------------------------
#
# Run the clean target only inside the sources directory. Compilation occurs in
# BUILD_DIR, not in WORK_DIR which is parent of BUILD_DIR and also contain cookies
# download, install etc. directories (thus no Makefile)
clean:
	@echo " DEBUG : Entering target clean from dft.mk"
	@echo "BUILD_DIR : $(BUILD_DIR)"
	pwd ;
	ls -lh $(BUILD_DIR)
	if [ -d $(BUILD_DIR)/ ] ; then make -C $(BUILD_DIR)/$(SW_NAME)-$(SW_VERSION) clean ; fi
	$(DISPLAY_COMPLETED_TARGET_NAME)


# ------------------------------------------------------------------------------
#
# Delete everthing from the work, cookies and download directories
#
mrproper:
	@echo "WORK_DIR : $(WORK_DIR)"
	@echo "SW_NAME : $(SW_NAME)"
	@echo "SW_VERSION : $(SW_VERSION)"
	@echo "would have executed : rm -rf $(WORK_DIR) --one-file-system --preserve-root"
#	@rm -rf "$(WORK_DIR)" --one-file-system --preserve-root
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
	@echo "  SW_LATEST                         $(SW_LATEST)" ;
	@if [ "$(DOWNLOAD_TOOL)" = "wget" ] ; then \
                echo "  SRC_DIST_FILES                    $(SRC_DIST_FILES)" ; \
                echo "  SRC_SIGN_FILES                    $(SRC_SIGN_FILES)" ; \
                echo "  SRC_DIST_URL                      $(SRC_DIST_URL)" ; \
	fi
	@if [ "$(DOWNLOAD_TOOL)" = 'git' ] ; then \
		echo "  GIT_URL                           $(GIT_URL)" ; \
		echo "  GIT_REPO                          $(GIT_REPO)" ; \
		echo "  GIT_REPO_EXT                      $(GIT_REPO_EXT)" ; \
		echo "  GIT_BRANCH                        $(GIT_BRANCH)" ; \
	fi
	@echo
	@echo "Packages upload parameters (using $(UPLOAD_TOOL))" ;
	@if [ "$(UPLOAD_TOOL)" = "scp" ] ; then \
                echo "  DFT_DEB_UPLOAD_SERVER             $(DFT_DEB_UPLOAD_SERVER)" ; \
                echo "  DFT_DEB_UPLOAD_PATH               $(DFT_DEB_UPLOAD_PATH)" ; \
                echo "  DFT_DEB_UPLOAD_USER               $(DFT_DEB_UPLOAD_USER)" ; \
	fi
	@echo
	@echo "Directories configuration"
	@echo "  DFT_BUILDSYSTEM                   $(DFT_BUILDSYSTEM)"
	@echo "  DFT_HOME                          $(DFT_HOME)"
	@echo "  DFT_FORGE                         $(DFT_FORGE)"
	@echo "  WORK_DIR                          $(WORK_DIR)"
	@echo "  FILE_DIR                          $(FILE_DIR)"
	@echo "  PATCH_DIR                         $(PATCH_DIR)"
	@echo "  DOWNLOAD_DIR                      $(DOWNLOAD_DIR)"
	@echo "  COOKIE_DIR                        $(COOKIE_DIR)"
	@echo "  BUILD_DIR                         $(BUILD_DIR)"
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
	@echo "  DEFAULT_DTB                       $(DEFAULT_DTB)"
	@echo "  KERNEL_DEFCONFIG                  $(KERNEL_DEFCONFIG)"
	@echo "  UBOOT_SUPPORT                     $(UBOOT_SUPPORT)"
	@echo "  UBOOT_DEFCONFIG                   $(UBOOT_DEFCONFIG)"
	@echo "  UBOOT_BINARY_FILE                 $(UBOOT_BINARY_FILE)"
	@echo "  GRUB_SUPPORT                      $(GRUB_SUPPORT)"
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

show-kernel-upstream-version:
	@wget -O-  https://www.kernel.org/ 2>&1| grep "<td><strong>" | tr '<' ' ' | tr '>' ' ' | awk '{ print $$3 }' | head -n 2 | tail -n 1

show-u-boot-upstream-version:
	@wget -O- https://github.com/u-boot/u-boot/releases 2>&1 | grep -v "rc" | grep "v20" | tr '<' ' ' | tr '>' ' ' | tr 'v' ' ' | head -n 2 | tail -n 1 | awk '{ print $$1 }'

# ------------------------------------------------------------------------------
# Match initial ifdef
endif
