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
	@echo "SOFTWARE_UPSTREAM_NAME     $(SOFTWARE_UPSTREAM_NAME)"
	@echo "SOFTWARE_VERSION           $(SOFTWARE_VERSION)"
	@echo "SOFTWARE_FULLNAME          $(SOFTWARE_FULLNAME)"
	@echo "SOFTWARE_SOURCE_FILES      $(SOFTWARE_SOURCE_FILES)"
	@echo
	@echo "GNU_PROJECT                $(GNU_PROJECT)"
	@echo
	@echo "x UPSTREAM_SOURCE_ACCESS : $(UPSTREAM_SOURCE_ACCESS)"
	@echo "x UPSTREAM_SOURCES_URL   : $(UPSTREAM_SOURCES_URL)"
	@echo
	@echo "x ALLFILES               : $(ALLFILES)"
	@echo
	@echo "x BUILD_SYSTEM_DIR       : $(BUILD_SYSTEM_DIR)"
	@echo "  Répertoire contenant le Makefile courant"
	@echo "x BASEDIR                : $(BASEDIR)"
	@echo "x WORKROOTDIR            : $(WORKROOTDIR)"
	@echo "x WORKDIR                : $(WORKDIR)"
	@echo "x FILEDIR                : $(FILEDIR)"
	@echo "x PATCHDIR               : $(PATCHDIR)"
	@echo "x DOWNLOADDIR            : $(DOWNLOADDIR)"
	@echo "x PARTIALDIR             : $(PARTIALDIR)"
	@echo "x COOKIEROOTDIR          : $(COOKIEROOTDIR)"
	@echo "x COOKIEDIR              : $(COOKIEDIR)"
	@echo "x EXTRACTDIR             : $(EXTRACTDIR)"
	@echo "x WORKSRC                : $(WORKSRC)"
	@echo "x OBJDIR                 : $(OBJDIR)"
	@echo "x INSTALLDIR             : $(INSTALLDIR)"
	@echo "x PKGDIR                 : $(PKGDIR)"
	@echo "x SCRATCHDIR             : $(SCRATCHDIR)"
	@echo "x TMPDIR                 : $(TMPDIR)"
	@echo "x TMPDIR_FULLPATH        : $(TMPDIR_FULLPATH)"
	@echo "x LOGDIR                 : $(LOGDIR)"
	@echo
	@echo "x CHECKSUM_FILE          : $(CHECKSUM_FILE)"
	@echo "x MANIFEST_FILE          : $(MANIFEST_FILE)"
	@echo
	@echo "x THIS_HOSTNAME          : $(THIS_HOSTNAME)"
	@echo "x THIS_ARCHITECTURE      : $(THIS_ARCHITECTURE)"
	@echo "x THIS_OPERATING_SYSTEM  : $(THIS_OPERATING_SYSTEM)"
	@echo "x THIS_OPERATING_SYSTEM_FLAVOR : $(THIS_OPERATING_SYSTEM_FLAVOR)"
	@echo
	@echo "x BUILD_ENV  : $(BUILD_ENV)"
	@echo "x BUILD_ARGS : $(BUILD_ARGS)"
	@echo
	@echo "x CONFIGURE_SCRIPTS      : $(CONFIGURE_SCRIPTS)"
	@echo "x 	BUILD_SCRIPTS          : $(BUILD_SCRIPTS)"


# ------------------------------------------------------------------------------
#
#   Fetch target is in charge of getting sources from a remote server or local 
#   file system. Files are copied into a local directory named files
#
#   This target only download files. Computing checksums and extracting files
#   are done by other targets.
#

# Construct the list of files path under downloaddir which will be processed by
# the $(DOWNLOADDIR)/% target
FETCH_TARGETS ?=  $(addprefix $(DOWNLOADDIR)/,$(DISTFILES))

fetch : prerequisite $(DOWNLOADDIR) $(COOKIEROOTDIR) pre-fetch $(FETCH_TARGETS) post-fetch
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

#
# TODO: Handle several sources for a file
#
$(DOWNLOADDIR)/% :
	@if test -f $(COOKIEDIR)/checksum-$* ; then \
		true ; \
	else \
		if [ "$(UPSTREAM_SOURCE_ACCESS)" = "wget" ] ; then \
			wget $(WGET_OPTS) -T 30 -c -P $(PARTIALDIR) $(UPSTREAM_SOURCES_URL)/$* ; \
			mv $(PARTIALDIR)/$* $@ ; \
			if test -r $@ ; then \
				true ; \
			else \
				echo 'ERROR : Failed to download $@!' 1>&2; \
				false; \
			fi; \
		else \
			echo "Fetch method $(UPSTREAM_SOURCE_ACCESS) is not implemented" ; \
		fi ; \
	fi ;


