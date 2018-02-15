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
Please replace "unknown" by the board architecture (arhmf, amd64, ppc64, etc.).


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

export DEBFULLNAME "John Doe"

endef
  $(error $(error_msg))
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

export DEBEMAIL "john@doe.org"

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
TARGET_DONE = @mkdir -p $(dir $(COOKIE_DIR)/$@) && touch $(COOKIE_DIR)/$@


# ------------------------------------------------------------------------------
#
# Determine this Makefile directory which is the root of the build system
#
BUILD_SYSTEM_ROOT := $(dir $(lastword $(MAKEFILE_LIST)))


# ------------------------------------------------------------------------------
#
# If not set, generate the distribution name based upon name and version
#
SOFTWARE_FULLNAME ?= $(SOFTWARE_UPSTREAM_NAME)-$(KERNEL_VERSION)


# ------------------------------------------------------------------------------
#
# Source retrieving tools and settings
#
UPSTREAM_DOWNLOAD_TOOL ?= wget


# ------------------------------------------------------------------------------
#
# Includes the build system top level variables definitions
#
# ------------------------------------------------------------------------------
include $(BUILD_SYSTEM_ROOT)/dft.conf.mk


# ------------------------------------------------------------------------------
#
# Includes the build system top level macros definitions
#
# ------------------------------------------------------------------------------
include $(BUILD_SYSTEM_ROOT)/dft.lib.mk


# ------------------------------------------------------------------------------
#
# Includes the build system configure definitions
#
# ------------------------------------------------------------------------------
include $(BUILD_SYSTEM_ROOT)/dft.configure.mk


# ------------------------------------------------------------------------------
#
# Includes the build system build definitions
#
# ------------------------------------------------------------------------------
include $(BUILD_SYSTEM_ROOT)/dft.build.mk


# ------------------------------------------------------------------------------
#
# Includes the build system install definitions
#
# ------------------------------------------------------------------------------
include $(BUILD_SYSTEM_ROOT)/dft.install.mk


# ------------------------------------------------------------------------------
#
# Includes the build system package definitions
#
# ------------------------------------------------------------------------------
include $(BUILD_SYSTEM_ROOT)/dft.package.mk


# ------------------------------------------------------------------------------
#
# Defines stub targets so that it is possible to define pre-something or
# post-something targets in Makefile. These pre/post will be automagically by
# targets even if not define thanks to stubs
#
# In addition a pre-everything target can be define and is run before the actual
# target
#
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
	@echo '   clean                   Delete the work directory and its contents'
	@echo '   distclean               Delete the root work directory and contents'
	@echo '   show-config(uration)    Echo the main configuration variable'
	@echo '   fetch                   Download software sources from upstream site'
	@echo '   fetch-list              Show list of files that would be retrieved by fetch'
	@echo '   checksum                Verify the checksums'
	@echo '   makesum(s)              Compute the checksums and create the checksum file'
	@echo '   extract                 Extract the contents of the files download by fetch target'
	@echo '   patch                   Apply the patchs listed in PATCHFILES'
	@echo '   configure               Execute the configure script'
	@echo '   build                   Build the software'
	@echo '   install                 Install the software to the target directory'
	@echo '   package                 Build the Debian package containing kernel or u-boot and all the related files'
	@echo
	@echo '   re[target]              Force execution of [target] even if already done (without execution of its depends)'

# ------------------------------------------------------------------------------
#
# Delete the work directory and its contents
#
clean:
	@rm -rf $(PARTIAL_DIR) $(WORK_DIR) $(INSTALL_DIR) $(PACKAGE_DIR) $(COOKIE_DIR)
	$(DISPLAY_COMPLETED_TARGET_NAME)


# ------------------------------------------------------------------------------
#
# Delete the root work directory and its contents
#
distclean:
	@rm -rf $(WORK_ROOT_DIR) $(COOKIE_DIR) $(DOWNLOAD_DIR)
	$(DISPLAY_COMPLETED_TARGET_NAME)


# ------------------------------------------------------------------------------
#
# Dump the values of the internal variables
#
show-configuration : show-config
show-config :
	@echo "Software configuration"
	@echo "  UPSTREAM_DOWNLOAD_TOOL            $(UPSTREAM_DOWNLOAD_TOOL)"
	@echo "  SOFTWARE_UPSTREAM_NAME            $(SOFTWARE_UPSTREAM_NAME)"
	@echo "  KERNEL_VERSION                    $(KERNEL_VERSION)"
	@echo "  KERNEL_FILE_VERSION               $(KERNEL_FILE_VERSION)"
	@echo "  KERNEL_BRANCH                     $(KERNEL_BRANCH)"
	@echo "  UBOOT_VERSION                     $(UBOOT_VERSION)"
	@echo "  UBOOT_TARGETS                     $(UBOOT_TARGETS)"
	@echo
	@echo "wget download parameters"
	@echo "  SOFTWARE_FULLNAME                 $(SOFTWARE_FULLNAME)"
	@echo "  SOFTWARE_DIST_FILES               $(SOFTWARE_DIST_FILES)"
	@echo "  SOFTWARE_SIGN_FILES               $(SOFTWARE_SIGN_FILES)"
	@echo "  KERNEL_SITE                       $(KERNEL_SITE)"
	@echo "  SOFTWARE_UPSTREAM_SITES           $(SOFTWARE_UPSTREAM_SITES)"
	@echo
	@echo "git download parameters"
	@echo "  KERNEL_GIT_URL                    $(KERNEL_GIT_URL)"
	@echo "  KERNEL_GIT_REPO                   $(KERNEL_GIT_REPO)"
	@echo "  KERNEL_GIT_REPO_EXT               $(KERNEL_GIT_REPO_EXT)"
	@echo "  KERNEL_GIT_BRANCH                 $(KERNEL_GIT_BRANCH)"
	@echo "  SOFTWARE_DIST_GIT                 $(SOFTWARE_DIST_GIT)"
	@echo
	@echo "Directories configuration"
	@echo "  BUILD_SYSTEM_ROOT                 $(BUILD_SYSTEM_ROOT)"
	@echo "  BASE_DIR                          $(BASE_DIR)"
	@echo "  WORK_ROOT_DIR                     $(WORK_ROOT_DIR)"
	@echo "  WORK_DIR                          $(WORK_DIR)"
	@echo "  FILE_DIR                          $(FILE_DIR)"
	@echo "  PATCH_DIR                         $(PATCH_DIR)"
	@echo "  DOWNLOAD_DIR                      $(DOWNLOAD_DIR)"
	@echo "  PARTIAL_DIR                       $(PARTIAL_DIR)"
	@echo "  COOKIE_DIR                        $(COOKIE_DIR)"
	@echo "  EXTRACT_DIR                       $(EXTRACT_DIR)"
	@echo "  WORK_SRC                          $(WORK_SRC)"
	@echo "  OBJ_DIR                           $(OBJ_DIR)"
	@echo "  INSTALL_DIR                       $(INSTALL_DIR)"
	@echo "  PACKAGE_DIR                       $(PACKAGE_DIR)"
	@echo "  TEMP_DIR                          $(TEMP_DIR)"
	@echo "  LOG_DIR                           $(LOG_DIR)"
	@echo "  CHECKSUM_FILE                     $(CHECKSUM_FILE)"
	@echo
	@echo "Build environnement"
	@echo "  BUILDER_ARCHITECTURE              $(BUILDER_ARCHITECTURE)"
	@echo "  BUILDER_HOSTNAME                  $(BUILDER_HOSTNAME)"
	@echo "  BUILDER_OPERATING_SYSTEM          $(BUILDER_OPERATING_SYSTEM)"
	@echo "  BUILDER_OPERATING_SYSTEM_FLAVOR   $(BUILDER_OPERATING_SYSTEM_FLAVOR)"
	@echo "  BUILDER_OPERATING_SYSTEM_VERSION  $(BUILDER_OPERATING_SYSTEM_VERSION)"
	@echo
	@echo "  CONFIGURE_SCRIPTS                 $(CONFIGURE_SCRIPTS)"
	@echo "  BUILD_SCRIPTS                     $(BUILD_SCRIPTS)"
	@echo
	@echo "  BOARD_NAME                        $(BOARD_NAME)"
	@echo "  USE_CONFIG_FILE                   $(USE_CONFIG_FILE)"
	@echo "  USE_DEFCONFIG                     $(USE_DEFCONFIG)"
	@echo "  DEFCONFIG_OVERRIDES               $(DEFCONFIG_OVERRIDES)"
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
	@echo "  FILTER_DIRS                       $(FILTER_DIRS)"

# ------------------------------------------------------------------------------
#
# Prerequisite target. Currently does nothing, should check for basic building
# packages to be avaiable. Should add a check based onthe flavor.
#

prerequisite : $(COOKIE_DIR) pre-everything
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)


# ------------------------------------------------------------------------------
#
#   Fetch target is in charge of getting sources from a remote server or local
#   file system. Files are copied into a local directory named files
#
#   This target only download files. Computing checksums and extracting files
#   are done by other targets.
#

# Construct the list of files path under downloaddir which will be processed by
# the $(DOWNLOAD_DIR)/% target
ifeq ($(UPSTREAM_DOWNLOAD_TOOL), wget)
FETCH_TARGETS ?=  $(addprefix $(DOWNLOAD_DIR)/,$(SOFTWARE_CHECKSUM_FILES)) $(addprefix $(DOWNLOAD_DIR)/,$(SOFTWARE_DIST_FILES))
else
ifeq ($(UPSTREAM_DOWNLOAD_TOOL), git)
FETCH_TARGETS ?=  $(addprefix $(GIT_EXTRACT_DIR)/,$(SOFTWARE_DIST_GIT))
else
define error_msg
Unknown UPSTREAM_DOWNLOAD_TOOL : $(UPSTREAM_DOWNLOAD_TOOL)
endef
$(error $(error_msg))
endif
endif

fetch-list:
	@echo $(FETCH_TARGETS)

fetch : prerequisite $(COOKIE_DIR) pre-fetch $(FETCH_TARGETS) post-fetch
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

$(DOWNLOAD_DIR)/% : $(DOWNLOAD_DIR) $(PARTIAL_DIR)
	@if test -f $(COOKIE_DIR)/$(DOWNLOAD_DIR)/$* ; then \
		true ; \
	else \
		wget $(WGET_OPTS) -T 30 -c -P $(PARTIAL_DIR) $(SOFTWARE_UPSTREAM_SITES)/$* ; \
		mv $(PARTIAL_DIR)/$* $@ ; \
		if test -r $@ ; then \
			true ; \
		else \
			echo 'ERROR : Failed to download $@!' 1>&2; \
			false; \
		fi; \
		if [ ! "" = "$(SOFTWARE_CHECKSUM_FILES)" ] ; then \
			if [ ! "$*" = "$(SOFTWARE_CHECKSUM_FILES)" ] ; then \
				if grep -- '$*' $(DOWNLOAD_DIR)/$(SOFTWARE_CHECKSUM_FILES) > /dev/null; then  \
					if cat $(DOWNLOAD_DIR)/$(SOFTWARE_CHECKSUM_FILES) | (cd $(DOWNLOAD_DIR); LC_ALL="C" LANG="C" md5sum -c 2>&1) | grep -- '$*' | grep -v ':[ ]\+OK' > /dev/null; then \
						echo "        \033[1m[Failed] : checksum of file $* is invalid\033[0m" ; \
						false; \
					else \
						echo "        [  OK   ] : $* checksum is valid	  " ; \
					fi ;\
				else  \
					echo "        \033[1m[Missing] : $* is not in the checksum file\033[0m $(DOWNLOAD_DIR)/$(SOFTWARE_CHECKSUM_FILES)" ; \
					false; \
				fi ; \
			fi ; \
		fi ; \
	fi ;
	$(TARGET_DONE)

$(GIT_EXTRACT_DIR)/% : $(GIT_EXTRACT_DIR)
	@if test -f $(COOKIE_DIR)/$(GIT_EXTRACT_DIR)/$* ; then \
		true ; \
	else \
		echo "        cloning into $(GIT_EXTRACT_DIR)/$*" ; \
		cd $(GIT_EXTRACT_DIR) ; \
        git clone --single-branch $(GIT_OPTS) -b $(KERNEL_GIT_BRANCH) $(KERNEL_GIT_URL)/$(KERNEL_GIT_REPO)$(KERNEL_GIT_REPO_EXT) ; \
	fi ;
	$(TARGET_DONE)


# ------------------------------------------------------------------------------
#
# Compare checksum file contents and current md5
#

CHECKSUM_TARGETS ?= $(addprefix checksum-,$(filter-out $(_NOCHECKSUM) $(NOCHECKSUM),$(SOFTWARE_DIST_FILES)))

checksum : fetch pre-checksum checksum_banner $(CHECKSUM_TARGETS) post-checksum
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

# Pretty output :)
checksum_banner :
	@echo "    running checksums"


# ------------------------------------------------------------------------------
#
# checksum utilities
#

# Check a given file's checksum against $(CHECKSUM_FILE) and error out if it
# mentions the file without an "OK".
checksum-% : $(CHECKSUM_FILE)
	@if grep -- '$*' $(CHECKSUM_FILE) > /dev/null; then  \
		if cat $(CHECKSUM_FILE) | (cd $(DOWNLOAD_DIR); LC_ALL="C" LANG="C" md5sum -c 2>&1) | grep -- '$*' | grep -v ':[ ]\+OK' > /dev/null; then \
			echo "        \033[1m[Failed] : checksum of file $* is invalid\033[0m" ; \
			false; \
		else \
			echo "        [  OK   ] : $*" ; \
		fi \
	else  \
		echo "        \033[1m[Missing] : $* is not in the checksum file\033[0m" ; \
		false ; \
	fi
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
#
# Create the checksum file if needed
#

$(CHECKSUM_FILE):
	@touch $(CHECKSUM_FILE)

# ------------------------------------------------------------------------------
#
# Remove the files identified in the NOCHECKSUM targets
#

MAKESUM_TARGETS ?=  $(filter-out $(_NOCHECKSUM) $(NOCHECKSUM),$(SOFTWARE_DIST_FILES))

# Check that the files really exist, even if they should be downloaded by
# fetch  target. Then call md5sum to generate checksum file
makesum  : pre-makesum fetch post-makesum
	@if test "x$(MAKESUM_TARGETS)" != "x"; then \
		(cd $(DOWNLOAD_DIR) && md5sum $(MAKESUM_TARGETS)) > $(CHECKSUM_FILE) ; \
		echo "    checksums made for $(MAKESUM_TARGETS)" ; \
		cat $(CHECKSUM_FILE) ; \
	else \
		cp /dev/null $(CHECKSUM_FILE) ; \
	fi

	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

# Provided for convenience
makesums : makesum


# ------------------------------------------------------------------------------
#
# Extract the contents of the files downloaded by the fetch target
#

# Construct the list of files path under downloaddir which will be processed by
# the $(DOWNLOAD_DIR)/% target
ifeq ($(UPSTREAM_DOWNLOAD_TOOL), wget)
EXTRACT_TARGETS ?=  $(addprefix extract-archive-,$(SOFTWARE_DIST_FILES))
else
ifeq ($(UPSTREAM_DOWNLOAD_TOOL), git)
EXTRACT_TARGETS ?=  $(addprefix extract-git-,$(SOFTWARE_DIST_GIT))
else
define error_msg
Unknown UPSTREAM_DOWNLOAD_TOOL : $(UPSTREAM_DOWNLOAD_TOOL)
endef
$(error $(error_msg))
endif
endif

extract : fetch $(EXTRACT_DIR) pre-extract $(EXTRACT_TARGETS) post-extract
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)


# ------------------------------------------------------------------------------
#
# Run the configure script
#

CONFIGURE_TARGETS ?= $(addprefix configure-,$(CONFIGURE_SCRIPTS))

configure : patch $(OBJ_DIR) pre-configure $(CONFIGURE_TARGETS) post-configure
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
# Appy patches to the sources
#

PATCH_TARGETS ?=  $(addprefix apply-patch-,$(PATCHFILES))

patch : extract pre-patch $(PATCH_TARGETS) post-patch
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)


# ------------------------------------------------------------------------------
#
# Build the target binaries
#

BUILD_TARGETS ?= $(addprefix build-,$(BUILD_CHECK_SCRIPTS)) $(addprefix build-,$(BUILD_SCRIPTS))

build : configure $(OBJ_DIR) pre-build $(BUILD_TARGETS) post-build
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)


# ------------------------------------------------------------------------------
#
# Rebuild the target binaries
#

REBUILD_TARGETS ?= $(addprefix rebuild-,$(BUILD_CHECK_SCRIPTS)) $(addprefix rebuild-,$(BUILD_SCRIPTS))

rebuild : configure pre-rebuild $(REBUILD_TARGETS) build post-rebuild
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)


# ------------------------------------------------------------------------------
#
# Install software to the target directory
#

install : build $(INSTALL_DIR) pre-install do-install post-install
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
#
# Execute once again the install target
#

reinstall : build pre-reinstall do-reinstall install post-reinstall
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)


# ------------------------------------------------------------------------------
#
# Build the Debian package
#

package : install $(PACKAGE_DIR) pre-package do-package post-package
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
#
# Execute once again the package target
#

repackage : install pre-repackage do-repackage package post-repackage
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)


