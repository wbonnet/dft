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
ifdef DFT_TARGET_FETCH
$(info target-fetch.mk has already been included)
else
DFT_TARGET_FETCH = 1

# Some temporary default values used to debug where where variables are initialized
SW_NAME     ?= out-of-scope
SW_VERSION  ?= out-of-scope

# ------------------------------------------------------------------------------
#
# Fetch target is in charge of getting idownloading sources from a remote server or local
# file system. Files are copied into a local directory identified by the DOWNLOAD_DIR
# variable. This target only download files. Computing checksums and extracting files
# are done by other targets.

# Construct the list of files to be fetched from the upstream site.
ifeq ($(DOWNLOAD_TOOL), wget)
  FETCH_TARGETS ?=  $(addprefix fetch-archive-,$(SRC_CHECKSUM_FILES)) $(addprefix fetch-archive-,$(SRC_DIST_FILES))
  else
    ifeq ($(DOWNLOAD_TOOL), git)
    FETCH_TARGETS ?=  $(addprefix clone-git-,$(SW_NAME))
    else
    define error_msg
Unknown DOWNLOAD_TOOL : $(DOWNLOAD_TOOL)
    endef
$(error $(error_msg))
    endif
endif

show-fetch-targets:
	@echo $(FETCH_TARGETS)

fetch : setup pre-fetch $(FETCH_TARGETS) post-fetch
	@for v in $(filter-out $(MAKE_FILTERS),$(shell find .  -mindepth 1 -maxdepth 1 -type d -printf '%P\n')) ; do \
		$(MAKE) --no-print-directory -C --directory=$$v $@ only-native-arch=$(only-native-arch) arch-warning=$(arch-warning); \
	done ;
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

# Some directories that will remain empty are created by dependancy mechanism
# To keep stuf clean the useless empty folders are removed by command rmdir
# --ignore-fail-on-non-empty
fetch-archive-%:
	skip_target=0 ; \
	if [ "$(SW_VERSION)" == "out-of-scope" ] ; then \
		skip_target=1 ; \
		true ; \
	fi; \
	if [ ! "x$(HOST_ARCH)" = "x$(BOARD_ARCH)" ] && [ "x$(only-native-arch)" = "x1" ] ; then \
		skip_target=1 ; \
	fi ; \
	if [ ! "x$$skip_target" = "x1" ] ; then \
		if [ -f $(COOKIE_DIR)/$@ ] ; then \
			true ; \
		else \
			wget --quiet $(WGET_OPTS) --timeout=30 --continue $(SRC_DIST_URL)/$* --directory-prefix=$(DOWNLOAD_DIR) ; \
			rmdir --ignore-fail-on-non-empty $(PARTIAL_DIR) ; \
			if [ -f $(DOWNLOAD_DIR)/$* ] ; then \
				true ; \
			else \
				echo 'ERROR : Failed to download $(SRC_DIST_URL)/$*' 1>&2; \
			        $(call dft_error ,2004-1602); \
			fi ; \
		fi ; \
	fi ;
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

clone-git-%:
	@skip_target=0 ; \
	if [ "$(SW_VERSION)" == "out-of-scope" ] ; then \
		skip_target=1 ; \
		true ; \
	fi; \
	if [ ! "x$(HOST_ARCH)" = "x$(BOARD_ARCH)" ] && [ "x$(only-native-arch)" = "x1" ] ; then \
		skip_target=1 ; \
	fi ; \
	if [ ! "x$$skip_target" = "x1" ] ; then \
		if [ -f $(COOKIE_DIR)/$@ ] ; then \
			true ; \
		else \
			echo "        cloning into $(GIT_DIR)/$*" ; \
			cd $(GIT_DIR) ; \
			git clone --single-branch $(GIT_OPTS) -b $(GIT_BRANCH) $(GIT_URL)/$(GIT_REPO)$(GIT_REPO_EXT) ; \
		fi ; \
	fi ;
	$(TARGET_DONE)

# Match initial ifdef DFT_TARGET_FETCH
endif
