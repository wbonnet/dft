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
ifdef DFT_TARGET_CHECKSUM
$(info target-checksum.mk has already been included)
else
#$(info now including target-checksum.mk)
DFT_TARGET_CHECKSUM = 1

# Some temporary default values used to debug where where variables are initialized
SW_NAME     ?= out-of-scope 
SW_VERSION  ?= out-of-scope

# ------------------------------------------------------------------------------
#
# Compare checksum file contents and current md5
#

CHECKSUM_TARGETS ?= $(addprefix checksum-,$(filter-out $(_NOCHECKSUM) $(NOCHECKSUM),$(SRC_DIST_FILES)))

checksum: fetch pre-checksum checksum_banner $(CHECKSUM_TARGETS) post-checksum
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

# Pretty output :)
checksum_banner:
	@echo "    running checksums"

# ------------------------------------------------------------------------------
#
# Checksum utilities
#

# Check a given file's checksum against $(CHECKSUM_FILE) and error out if it
# mentions the file without an "OK".
checksum-%: $(CHECKSUM_FILE)
	@if [ "$(SW_VERSION)" == "out-of-scope" ] ; then \
		true ; \
	else \
		if grep -- '$*' $(CHECKSUM_FILE) > /dev/null; then \
			if cat $(CHECKSUM_FILE) | (cd $(DOWNLOAD_DIR); LC_ALL="C" LANG="C" md5sum -c 2>&1) | grep -- '$*' | grep -v ':[ ]\+OK' > /dev/null ; then \
				echo "        [Failed] : checksum of file $* is invalid" ; \
				false; \
			else \
				echo "        [  OK   ] : $*" ; \
			fi \
		else  \
			echo "        [Missing] : $* is not in the checksum file" ; \
			false ; \
		fi ; \
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

MAKESUM_TARGETS ?=  $(filter-out $(_NOCHECKSUM) $(NOCHECKSUM),$(SRC_DIST_FILES))

# Check that the files really exist, even if they should be downloaded by
# fetch  target. Then call md5sum to generate checksum file
makesum: pre-makesum fetch post-makesum
	@if [ "x$(MAKESUM_TARGETS)" != "x" ] ; then \
		(cd $(DOWNLOAD_DIR) && md5sum $(MAKESUM_TARGETS)) > $(CHECKSUM_FILE) ; \
		echo "    checksums made for $(MAKESUM_TARGETS)" ; \
		cat $(CHECKSUM_FILE) ; \
	else \
		cp /dev/null $(CHECKSUM_FILE) ; \
	fi

	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

# Provided for convenience
makesums: makesum

# Match initial ifdef DFT_TARGET_CHECKSUM
endif
