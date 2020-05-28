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
TARGET_DONE = @mkdir -p $(COOKIE_DIR) && touch -a $(COOKIE_DIR)/$(notdir $@)

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
	@echo "   show-config             Display the build system configuration and values of internal variables"
	@echo "   fetch                   Download software sources from upstream site"
	@echo "   fetch-list              Show list of files that would be retrieved by fetch"
	@echo "   checksum                Compare the checksums of downloaded files to the content of checksums file"
	@echo "   makesum(s)              Compute the checksums and create the checksum file"
	@echo "   extract                 Extract the content of the files downloaded by fetch target"
	@echo "   patch                   Apply the patches identified by the PATCHFILES Makefile variable"
	@echo "   configure               Execute the configure script"
	@echo "   build                   Build the software from sources"
	@echo "   install                 Install the software to the target directory under workdir"
	@echo "   bsp[-package] | package Build all versions of BSP software packages (both linux kernel and u-boot)"
	@echo "   u-boot-package          Build all versions of u-boot package (and only u-boot, thus no kernel)"
	@echo "                           for board $(BOARD_NAME)"
	@echo "   kernel-package          Build all versions of linux kernel package (and only linux kernel, thus no u-boot)"
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
	@echo "                           Since cross compilation is not supported, to build binaries for different arch"
	@echo "                           you need at least one builder per arch and to collect generated .deb files"
	@echo "                           "
	@echo "   help                    Display this help"
	@echo "   help-config             Display help about global environment and configuration variables"
	@echo "                           "
	@echo "                           "
	@echo "                           While recursively walking the tree of category and board, make encounters targets using"
	@echo "                           a CPU architecture different from the one make and build toolchain are running on."
	@echo "                           The following command line variables can be used to control make behavior when dealing"
	@echo "                           with arch dependant targets:"
	@echo "                           "
	@echo "                           arch-warning=0     (display warning when skipping a target because of arch"
	@echo "                                               compatibility. default value=0)"
	@echo "                           only-native-arch=1 (skip all targets, it means no dowload nor extract, if builder"
	@echo "                                               arch is different from target board arch. You need a distinct"
	@echo "                                               builder per hardware arch. default value=0)"
	@echo "                           "
	@echo "   The following targets are recursive and available only if write access to buildsystem is granted. New files"
	@echo "   and folders will be created under buildsystem during execution. New items will not be added automatically to git."
	@echo "   git add has to be done manually, depending on you workspace, as the pull request if needed by the git server."
	@echo "                           "
	@echo "   add-u-boot-version      new-version=YYYY.MM (require write acess)"
	@echo "                           Create a new supported u-boot version entry. ex: make add-u-boot-version new-version=2019.07"
	@echo "                           This target will create a subdirectory named after the content of the new-version variable."
	@echo "                           It will contain the Makefile and all the files needed to fetch and build the given"
	@echo "                           version. It also instanciate Debian package template."
	@echo "                           "
	@echo "   check-u-boot-defconfig  Check defconfig target availability from upstream sources"

help-config:
	@echo "Writting is in progress, please come back in a couple of days or so"

# ------------------------------------------------------------------------------
#
# Run the clean target only inside the sources directory. Compilation occurs in
# BUILD_DIR, not in WORK_DIR which is parent of BUILD_DIR and also contain cookies
# download, install etc. directories (thus no Makefile)
#	if [ -d $(BUILD_DIR)/$(SW_NAME)-$(SW_VERSION) ] ; then rmdir $(BUILD_DIR)/$(SW_NAME)-$(SW_VERSION) ; fi
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
	@echo "WORKDIR : $(WORK_DIR)"
	@echo "SW_NAME : $(SW_NAME)"
	@echo "SW_VERSION : $(SW_VERSION)"
	@echo "rm -rf $(WORK_DIR) --one-file-system --preserve-root"
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
	@echo "  DFT_WORKSPACE                     $(DFT_WORKSPACE)"
	@echo "  WORK_DIR                          $(WORK_DIR)"
	@echo "  FILE_DIR                          $(FILE_DIR)"
	@echo "  DEFCONFIG_DIR                     $(DEFCONFIG_DIR)"
	@echo "  PATCH_DIR                         $(PATCH_DIR)"
	@echo "  DOWNLOAD_DIR                      $(DOWNLOAD_DIR)"
	@echo "  PARTIAL_DIR                       $(PARTIAL_DIR)"
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
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
# Match initial ifdef
endif
