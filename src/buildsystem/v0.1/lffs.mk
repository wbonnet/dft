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
#
# Copyright 2014 LFFS project (http://www.linuxfirmwarefromscratch.org).  
# All rights reserved. Use is subject to license terms.
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
#
# Contributors list :
#
#    William Bonnet 	wllmbnnt@gmail.com
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
# Used for output...
#
DISPLAY_TARGET_NOT_IMPLEMENTED = @echo "Target [$@] is not implemented !"
DISPLAY_COMPLETED_TARGET_NAME  = @echo "    completed [$@] "


# ------------------------------------------------------------------------------
#
# Cookie maker
#
TARGET_DONE = @mkdir -p $(dir $(COOKIEROOTDIR)/$@) && touch $(COOKIEROOTDIR)/$@

# ------------------------------------------------------------------------------
#
# Determine this Makefile directory which is the root of the build system
# 
BUILD_SYSTEM_ROOT := $(dir $(lastword $(MAKEFILE_LIST)))


# ------------------------------------------------------------------------------
#
# If not set, generate the distribution name based upon name and version
#
SOFTWARE_FULLNAME ?= $(SOFTWARE_UPSTREAM_NAME)-$(SOFTWARE_VERSION)


# ------------------------------------------------------------------------------
#
# Source retrieving tools and settings
#
UPSTREAM_SOURCE_ACCESS_TOOL ?= wget


# ------------------------------------------------------------------------------
#
# Includes the build system top level variables definitions
#
# ------------------------------------------------------------------------------
include $(BUILD_SYSTEM_ROOT)/lffs.conf.mk


# ------------------------------------------------------------------------------
#
# Includes the build system top level macros definitions
#
# ------------------------------------------------------------------------------
include $(BUILD_SYSTEM_ROOT)/lffs.lib.mk


# ------------------------------------------------------------------------------
#
# Includes the build system configure definitions
#
# ------------------------------------------------------------------------------
include $(BUILD_SYSTEM_ROOT)/lffs.configure.mk


# ------------------------------------------------------------------------------
#
# Includes the build system build definitions
#
# ------------------------------------------------------------------------------
include $(BUILD_SYSTEM_ROOT)/lffs.build.mk


# ------------------------------------------------------------------------------
#
# Includes the build system install definitions
#
# ------------------------------------------------------------------------------
include $(BUILD_SYSTEM_ROOT)/lffs.install.mk


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
	@echo 


# ------------------------------------------------------------------------------
#
# Delete the work directory and its contents
#
clean: 
	@rm -rf $(PARTIALDIR) $(WORKDIR) $(INSTALLDIR) $(PACKAGEDIR) $(COOKIEROOTDIR) 
	$(DISPLAY_COMPLETED_TARGET_NAME)


# ------------------------------------------------------------------------------
#
# Delete the root work directory and its contents
#
distclean: 
	@rm -rf $(WORKROOTDIR) $(COOKIEROOTDIR) $(DOWNLOADDIR)
	$(DISPLAY_COMPLETED_TARGET_NAME)


# ------------------------------------------------------------------------------
#
# Dump the values of the internal variables
#
show-configuration : show-config
show-config :
	@echo "Software configuration"
	@echo "  SOFTWARE_UPSTREAM_NAME            $(SOFTWARE_UPSTREAM_NAME)"
	@echo "  SOFTWARE_VERSION                  $(SOFTWARE_VERSION)"
	@echo "  SOFTWARE_FULLNAME                 $(SOFTWARE_FULLNAME)"
	@echo "  SOFTWARE_SOURCE_FILES             $(SOFTWARE_SOURCE_FILES)"
	@echo
	@echo "  GNU_PROJECT                       $(GNU_PROJECT)"
	@echo "  SF_PROJECT                        $(SF_PROJECT)"
	@echo
	@echo "x UPSTREAM_SOURCE_ACCESS            $(UPSTREAM_SOURCE_ACCESS)"
	@echo "x UPSTREAM_SOURCES_URL              $(UPSTREAM_SOURCES_URL)"
	@echo
	@echo "x ALL_FILES                         $(ALL_FILES)"
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
	@echo "  COOKIE_ROOT_DIR                   $(COOKIE_ROOT_DIR)"
	@echo "  COOKIE_DIR                        $(COOKIE_DIR)"
	@echo "  EXTRACT_DIR                       $(EXTRACT_DIR)"
	@echo "  WORK_SRC                          $(WORK_SRC)"
	@echo "  OBJ_DIR                           $(OBJ_DIR)"
	@echo "  INSTALL_DIR                       $(INSTALL_DIR)"
	@echo "  TEMP_DIR                          $(TEMP_DIR)"
	@echo "  TEMP_DIR_FULL_PATH                $(TEMP_DIR_FULL_PATH)"
	@echo "  LOG_DIR                           $(LOG_DIR)"
	@echo
	@echo "  CHECKSUM_FILE                     $(CHECKSUM_FILE)"
	@echo
	@echo "  BUILDER_ARCHITECTURE              $(BUILDER_ARCHITECTURE)"
	@echo "  BUILDER_HOSTNAME                  $(BUILDER_HOSTNAME)"
	@echo "  BUILDER_OPERATING_SYSTEM          $(BUILDER_OPERATING_SYSTEM)"
	@echo "  BUILDER_OPERATING_SYSTEM_FLAVOR   $(BUILDER_OPERATING_SYSTEM_FLAVOR)"
	@echo "  BUILDER_OPERATING_SYSTEM_VERSION  $(BUILDER_OPERATING_SYSTEM_VERSION)"
	@echo
	@echo "x BUILD_ENV                         $(BUILD_ENV)"
	@echo "x BUILD_ARGS                        $(BUILD_ARGS)"
	@echo
	@echo "x CONFIGURE_SCRIPTS                 $(CONFIGURE_SCRIPTS)"
	@echo "x BUILD_SCRIPTS                     $(BUILD_SCRIPTS)"


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
FETCH_TARGETS ?=  $(addprefix $(DOWNLOAD_DIR)/,$(DISTFILES))

fetch : prerequisite $(DOWNLOAD_DIR) $(COOKIE_ROOT_DIR) pre-fetch $(FETCH_TARGETS) post-fetch
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

#
# TODO: Handle several sources for a file
#
$(DOWNLOAD_DIR)/% :
	@if test -f $(COOKIE_DIR)/checksum-$* ; then \
		true ; \
	else \
		if [ "$(UPSTREAM_SOURCE_ACCESS_TOOL)" = "wget" ] ; then \
			wget $(WGET_OPTS) -T 30 -c -P $(PARTIAL_DIR) $(UPSTREAM_SOURCES_URL)/$* ; \
			mv $(PARTIAL_DIR)/$* $@ ; \
			if test -r $@ ; then \
				true ; \
			else \
				echo 'ERROR : Failed to download $@!' 1>&2; \
				false; \
			fi; \
		else \
			echo "Fetch method $(UPSTREAM_SOURCE_ACCESS_TOOL) is not implemented" ; \
		fi ; \
	fi ;


