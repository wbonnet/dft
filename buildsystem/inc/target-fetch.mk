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
#$(info now including target-fetch.mk)
DFT_TARGET_FETCH = 1

# Some temporary default values used to debug where where variables are initialized
SW_NAME     ?= no-name-at-target-fetch
SW_VERSION  ?= no-version-at-target-fetch

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
	@echo "DEBUG : SW_VERSION :$(SW_VERSION):" ;
endif

show-fetch-targets:
	@echo $(FETCH_TARGETS)

fetch : setup $(COOKIE_DIR) $(DOWNLOAD_DIR) $(PARTIAL_DIR) pre-fetch $(FETCH_TARGETS) post-fetch
	@echo "DEBUG : match fetch in target-fetch.mk => was supposed to do $(FETCH_TARGETS)" ;
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

fetch-archive-%: $(DOWNLOAD_DIR) $(PARTIAL_DIR)
	@echo "DEBUG : match fetch-archive-$* in target-fetch.mk" ; 
	if [ "$(SW_VERSION)" = "" ] ; then \
		echo "D3BUG : SW_VERSION is empty of undefined. Not at a defined version level skiping fetch " ; \
		echo "plop je suis la" ; \
		pwd ; \
		exit 0 ; \
	else \
		echo "DEBUG : AROBASE :$@ : expected full fetch-archive-v_machin" ; \
		echo "DEBUG : ETOILE  :$* : expected que_le_v_machin" ; \
		if [ -f $(COOKIE_DIR)/$@ ] ; then \
			true ; \
		else \
			wget $(WGET_OPTS) -T 30 -c -P $(PARTIAL_DIR) $(SRC_DIST_URL)/$* ; \
			mv $(PARTIAL_DIR)/$* $(DOWNLOAD_DIR) ; \
			rmdir --ignore-fail-on-non-empty $(PARTIAL_DIR) ; \
			if [ -f $(DOWNLOAD_DIR)/$* ] ; then \
				true ; \
			else \
				echo 'ERROR : Failed to download $(SRC_DIST_URL)/$*' 1>&2; \
				exit 0; \
			fi ; \
			if [ ! "" = "$(SRC_CHECKSUM_FILES)" ] ; then \
				if [ ! "$*" = "$(SRC_CHECKSUM_FILES)" ] ; then \
					if grep -- '$*' $(DOWNLOAD_DIR)/$(SRC_CHECKSUM_FILES) > /dev/null ; then \
						if cat $(DOWNLOAD_DIR)/$(SRC_CHECKSUM_FILES) | (cd $(DOWNLOAD_DIR); LC_ALL="C" LANG="C" md5sum -c 2>&1) | grep -- '$*' | grep -v ':[ ]\+OK' > /dev/null; then \
							echo "        [Failed] : checksum of file $r*@ is invalid" ; \
							false; \
						else \
							echo "        [  OK   ] : $* checksum is valid	  " ; \
						fi ; \
					else \
						echo "        [Missing] : $* is not in the checksum file $(DOWNLOAD_DIR)/$(SRC_CHECKSUM_FILES)" ; \
						exit 1 ; \
					fi ; \
				fi ; \
			fi ; \
		fi ; \
	fi ; 
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

clone-git-%: $(GIT_DIR)
	@if [ -f $(COOKIE_DIR)/$(GIT_DIR)/$@ ] ; then 
		true ; 
	else 
		echo "        cloning into $(GIT_DIR)/$*" ; 
		cd $(GIT_DIR) ; 
		git clone --single-branch $(GIT_OPTS) -b $(GIT_BRANCH) $(GIT_URL)/$(GIT_REPO)$(GIT_REPO_EXT) ; 
	fi ;
	$(TARGET_DONE)

# Match initial ifdef DFT_TARGET_FETCH
endif
