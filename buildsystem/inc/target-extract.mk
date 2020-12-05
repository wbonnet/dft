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
# Copyright 2019 DFT project (http://www.firmwaretoolkit.org).
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
ifdef DFT_TARGET_EXTRACT
$(info target-extract.mk has already been included)
else
DFT_TARGET_EXTRACT = 1

# ------------------------------------------------------------------------------
#
# Extract the contents of the files downloaded by the fetch target
#

# Construct the list of files path under downloaddir which will be processed by
# the $(DOWNLOAD_DIR)/% target
ifeq ($(DOWNLOAD_TOOL), wget)
EXTRACT_TARGETS ?=  $(addprefix extract-archive-,$(SRC_DIST_FILES))
else
ifeq ($(DOWNLOAD_TOOL), git)
EXTRACT_TARGETS ?=  $(addprefix extract-git-,$(SW_NAME))
else
define error_msg
Unknown DOWNLOAD_TOOL : $(DOWNLOAD_TOOL)
endef
$(error $(error_msg))
endif
endif

extract: fetch pre-extract $(EXTRACT_TARGETS) post-extract
	@if [ "$(only-latest)" = "1" ] ; then \
		if [ ! "$(SW_LATEST)" = "" ] ; then \
			cd $(SW_LATEST) && $(MAKE) --no-print-directory $@ only-native-arch=$(only-native-arch) arch-warning=$(arch-warning) only-latest=$(only-latest) verbosity=$(verbosity) && cd .. ;  \
		fi ; \
	else \
		pwd ; \
		for v in extract_debug $(filter-out $(MAKE_FILTERS),$(shell find .  -mindepth 1 -maxdepth 1 -type d -printf '%P\n')) ; \
			do echo "target-extract iterateur extract_debug : $$v" ; \
		done ; \
	fi ;
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
#
# archive extraction utilities
#
TAR_ARGS = --no-same-owner

show-extract-targets:
	@pwd ;
	@echo $(EXTRACT_TARGETS)

extract-archive-v.tar:
extract-archive-%.tar:
	@if [ ! "$(SW_VERSION)" = "" ] ; then \
		if [ ! "$(SW_VERSION)" == "undefined-sw-version" ] ; then \
			if [ ! -f $(COOKIE_DIR)/$@ ] ; then \
				if [ "$(verbosity)" == "1" ] ; then \
					echo "        extracting $(DOWNLOAD_DIR)/$*.tar" ; \
				fi ; \
				tar $(TAR_ARGS) -xf $(DOWNLOAD_DIR)/$*.tar -C $(BUILD_DIR) ; \
			fi ; \
		fi ;
	fi ;
	$(TARGET_DONE)

extract-archive-v.tar.gz:
extract-archive-%.tar.gz:
	@if [ !  "$(SW_VERSION)" = "" ] ; then \
		if [ ! "$(SW_VERSION)" == "undefined-sw-version" ] ; then \
			if [ ! -f $(COOKIE_DIR)/$@ ] ; then \
				if [ ! -f $(DOWNLOAD_DIR)/$*.tar.gz ] ; then \
						echo "        archive $(DOWNLOAD_DIR)/$*.tar.gz is missing please check the files retrieved by the fetch target" ; \
				fi ; \
				if [ "$(verbosity)" == "1" ] ; then \
					echo "        extracting $(DOWNLOAD_DIR)/$*.tar.gz" ; \
				fi ; \
				tar $(TAR_ARGS) -xzf $(DOWNLOAD_DIR)/$*.tar.gz -C $(BUILD_DIR) ; \
				mv $(BUILD_DIR)/$(SW_NAME)-$(SW_VERSION)/* $(BUILD_DIR) ; \
				rm -fr $(BUILD_DIR)/$(SW_NAME)-$(SW_VERSION) ; \
			fi ; \
		fi ; \
	fi ;
	$(TARGET_DONE)

extract-archive-v.tgz:
extract-archive-%.tgz:
	@if [ !"$(SW_VERSION)" = "" ] ; then \
		if [ ! "$(SW_VERSION)" == "undefined-sw-version" ] ; then \
			if [ ! -f $(COOKIE_DIR)/$@ ] ; then \
				if [ ! -f $(DOWNLOAD_DIR)/$*.tgz ] ; then \
						echo "        archive $(DOWNLOAD_DIR)/$*.tgz is missing please check the files retrieved by the fetch target" ; \
				fi ; \
				if [ "$(verbosity)" == "1" ] ; then \
					echo "        extracting $(DOWNLOAD_DIR)/$*.tgz" ; \
				fi ; \
				tar $(TAR_ARGS) -xzf $(DOWNLOAD_DIR)/$*.tgz -C $(BUILD_DIR) ; \
				mv $(BUILD_DIR)/$(SW_NAME)-$(SW_VERSION)/* $(BUILD_DIR) ; \
				rm -fr $(BUILD_DIR)/$(SW_NAME)-$(SW_VERSION) ; \
			fi ; \
		fi ; \
	fi ;
	$(TARGET_DONE)

extract-archive-v.tar.bz2:
extract-archive-%.tar.bz2:
	@if [ ! "$(SW_VERSION)" = "" ] ; then \
		if [ ! "$(SW_VERSION)" == "undefined-sw-version" ] ; then \
			if [ ! -f $(COOKIE_DIR)/$@ ] ; then \
				if [ "$(verbosity)" == "1" ] ; then \
					echo "        extracting $(DOWNLOAD_DIR)/$*.tar.bz2" ; \
				fi ; \
				tar $(TAR_ARGS) -xjf $(DOWNLOAD_DIR)/$*.tar.bz2 -C $(BUILD_DIR) ; \
				mv $(BUILD_DIR)/$(SW_NAME)-$(SW_VERSION)/* $(BUILD_DIR) ; \
				rm -fr $(BUILD_DIR)/$(SW_NAME)-$(SW_VERSION) ; \
			fi ; \
		fi ; \
	fi ;
	$(TARGET_DONE)

extract-archive-v.tar.xz:
extract-archive-%.tar.xz:
	@if [ ! "$(SW_VERSION)" = "" ] ; then \
		if [ ! "$(SW_VERSION)" == "undefined-sw-version" ] ; then \
			if [ ! -f $(COOKIE_DIR)/$@ ] ; then \
				if [ "$(verbosity)" == "1" ] ; then \
					echo "        extracting $(DOWNLOAD_DIR)/$*.tar.xz" ; \
				fi ; \
				tar $(TAR_ARGS) -xJf $(DOWNLOAD_DIR)/$*.tar.xz -C $(BUILD_DIR) ; \
				mv $(BUILD_DIR)/$(SW_NAME)-$(SW_VERSION)/* $(BUILD_DIR) ; \
				rm -fr $(BUILD_DIR)/$(SW_NAME)-$(SW_VERSION) ; \
			fi ; \
		fi ; \
	fi ;
	$(TARGET_DONE)

extract-archive-v.zip:
extract-archive-%.zip:
	@if [ ! "$(SW_VERSION)" = "" ] ; then \
		if [ ! "$(SW_VERSION)" == "undefined-sw-version" ] ; then \
			if [ ! -f $(COOKIE_DIR)/$@ ] ; then \
				if [ "$(verbosity)" == "1" ] ; then \
					echo "        extracting $(DOWNLOAD_DIR)/$*.zip" ; \
				fi ; \
				unzip $(DOWNLOAD_DIR)/$*.zip -d $(BUILD_DIR) ; \
				mv $(BUILD_DIR)/$(SW_NAME)-$(SW_VERSION)/* $(BUILD_DIR) ; \
				rm -fr $(BUILD_DIR)/$(SW_NAME)-$(SW_VERSION) ; \
			fi ; \
		fi ; \
	fi ;
	$(TARGET_DONE)

extract-git-v:
extract-git-%:
	@if [ ! "$(SW_VERSION)" = "" ] ; then \
		if [ ! "$(SW_VERSION)" == "undefined-sw-version" ] ; then \
			if [ ! -f $(COOKIE_DIR)/$@ ] ; then \
				if [ "$(verbosity)" == "1" ] ; then \
		  			echo "        moving git data to $(EXTRACT)/$*" ; \
				fi ; \
			mv $(GIT_BUILD_DIR)/$(SRC_GIT_REPO)/* $(BUILD_DIR)/ ; \
			fi ; \
		fi ; \
	fi ;
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
#
# patch utilities
#
PATCH_DIR_LEVEL ?= 1
PATCH_DIR_FUZZ  ?= 2
PATCH_ARGS       = --directory=$(WORK_DIR) --strip=$(PATCH_DIR_LEVEL) --fuzz=$(PATCH_DIR_FUZZ)

apply-patch-%:
	@if [ !"$(SW_VERSION)" = "" ] ; then \
		if [ ! "$(SW_VERSION)" == "undefined-sw-version" ] ; then \
			if [ "$(verbosity)" == "1" ] ; then \
				echo " ==> Applying $(PATCH_DIR)/$*"
			fi ; \
			patch $(PATCH_ARGS) < $(PATCH_DIR)/$*
		fi ; \
	fi ;
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
#
# Appy patches to the sources
#

PATCH_TARGETS ?=  $(addprefix apply-patch-,$(PATCHFILES))

patch: extract pre-patch $(PATCH_TARGETS) post-patch
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

# Match initial ifdef DFT_TARGET_EXTRACT
endif

