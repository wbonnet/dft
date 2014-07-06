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
# archive extraction utilities
#
TAR_ARGS = --no-same-owner

extract-archive-%.tar : 
	@echo "        extracting $(DOWNLOAD_DIR)/$*.tar"
	@tar $(TAR_ARGS) -xf $(DOWNLOAD_DIR)/$*.tar -C $(EXTRACT_DIR)
	$(TARGET_DONE)

extract-archive-%.tar.gz : 
	@echo "        extracting $(DOWNLOAD_DIR)/$*.tar.gz"
	@tar $(TAR_ARGS) -xzf $(DOWNLOAD_DIR)/$*.tar.gz -C $(EXTRACT_DIR)
	$(TARGET_DONE)

extract-archive-%.tgz : 
	@echo "        extracting $(DOWNLOAD_DIR)/$*.tgz"
	@tar $(TAR_ARGS) -xzf $(DOWNLOAD_DIR)/$*.tgz -C $(EXTRACT_DIR)
	$(TARGET_DONE)

extract-archive-%.tar.bz2 : 
	@echo "        extracting $(DOWNLOAD_DIR)/$*.tar.bz2"
	@tar $(TAR_ARGS) -xjf $(DOWNLOAD_DIR)/$*.tar.bz2 -C $(EXTRACT_DIR)
	$(TARGET_DONE)

extract-archive-%.tar.xz : 
	@echo "        extracting $(DOWNLOAD_DIR)/$*.tar.xz"
	@tar $(TAR_ARGS) -xJf $(DOWNLOAD_DIR)/$*.tar.xz -C $(EXTRACT_DIR)
	$(TARGET_DONE)	

extract-archive-%.zip : 
	@echo "        extracting $(DOWNLOAD_DIR)/$*.zip"
	@unzip $(DOWNLOAD_DIR)/$*.zip -d $(EXTRACT_DIR)
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
#
# patch utilities
#
PATCH_DIR_LEVEL ?= 0
PATCH_DIR_FUZZ  ?= 2
PATCH_ARGS       = --directory=$(WORK_SRC) --strip=$(PATCH_DIR_LEVEL) --fuzz=$(PATCH_DIR_FUZZ)

apply-patch-% : 
	@echo " ==> Applying $(PATCH_DIR)/$*"
	patch $(PATCH_ARGS) < $(PATCH_DIR)/$*
	$(TARGET_DONE)

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
		false; \
	fi
	$(TARGET_DONE)

$(CHECKSUM_FILE):
	@touch $(CHECKSUM_FILE)

