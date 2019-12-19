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
# Protection against multiple includes
#
ifdef DFT_BUILDSYSTEM_TARGET_FETCH
$(error target-fetch.mk has already been included)
else
define DFT_BUILDSYSTEM_TARGET_FETCH
endef
# the matching endif teminates this file

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
#
ifeq ($(DOWNLOAD_TOOL), wget)
FETCH_TARGETS ?=  $(addprefix fetch-wget-,$(SRC_CHECKSUM_FILES)) $(addprefix fetch-wget-,$(SRC_DIST_FILES))
else
ifeq ($(DOWNLOAD_TOOL), git)
FETCH_TARGETS ?=  $(addprefix fetch-git-,$(SW_NAME))
else
define error_msg
Unknown DOWNLOAD_TOOL : $(DOWNLOAD_TOOL)
endef
$(error $(error_msg))
endif
endif

fetch-list:
	@echo $(FETCH_TARGETS)

fetch: setup $(COOKIE_DIR) pre-fetch $(FETCH_TARGETS) post-fetch
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

fetch-wget-%: $(DOWNLOAD_DIR) $(PARTIAL_DIR)
	if test -f $(COOKIE_DIR)/$* ; then \
		true ; \
	else \
		wget $(WGET_OPTS) -T 30 -c -P $(PARTIAL_DIR) $(SRC_DIST_URL)/$* ; \
		mv $(PARTIAL_DIR)/$* $(DOWNLOAD_DIR) ; \
		rmdir --ignore-fail-on-non-empty $(PARTIAL_DIR) ; \
		tree $(DOWNLOAD_DIR) ; \
		if test -f $(DOWNLOAD_DIR)/$* ; then \
			true ; \
		else \
			echo 'ERROR : Failed to download $@!' 1>&2; \
			false; \
		fi; \
		if [ ! "" = "$(SRC_CHECKSUM_FILES)" ] ; then \
			if [ ! "$*" = "$(SRC_CHECKSUM_FILES)" ] ; then \
				if grep -- '$*' $(DOWNLOAD_DIR)/$(SRC_CHECKSUM_FILES) > /dev/null ; then  \
					if cat $(DOWNLOAD_DIR)/$(SRC_CHECKSUM_FILES) | (cd $(DOWNLOAD_DIR); LC_ALL="C" LANG="C" md5sum -c 2>&1) | grep -- '$*' | grep -v ':[ ]\+OK' > /dev/null; then \
						echo "        \033[1m[Failed] : checksum of file $* is invalid\033[0m" ; \
						false; \
					else \
						echo "        [  OK   ] : $* checksum is valid	  " ; \
					fi ;\
				else  \
					echo "        \033[1m[Missing] : $* is not in the checksum file\033[0m $(DOWNLOAD_DIR)/$(SRC_CHECKSUM_FILES)" ; \
					false; \
				fi ; \
			fi ; \
		fi ; \
	fi ;
	$(TARGET_DONE)

fetch-git-%: $(GIT_DIR)
	if test -f $(COOKIE_DIR)/$(GIT_DIR)/$* ; then \
		true ; \
	else \
		echo "        cloning into $(GIT_DIR)/$*" ; \
		cd $(GIT_DIR) ; \
        git clone --single-branch $(GIT_OPTS) -b $(GIT_BRANCH) $(GIT_URL)/$(GIT_REPO)$(GIT_REPO_EXT) ; \
	fi ;
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
# Match initial ifdef
endif

