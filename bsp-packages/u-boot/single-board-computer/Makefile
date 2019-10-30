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
# Copyright 2019 DFT project (http://www.debianfirmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#

# Do not recurse the following subdirs
FILTER_DIRS  = . 

# ------------------------------------------------------------------------------
#
# Targets not associated with a file (aka PHONY)
#
.PHONY: help

# Catch all target. Call the same targets in each subfolder
%:
	@for i in $(filter-out $(FILTER_DIRS),$(shell find . -maxdepth 1 -type d )) ; do \
		$(MAKE) -C $$i $* || exit 1 ; \
done

check:
	for i in $(filter-out $(FILTER_DIRS),$(shell find . -maxdepth 1 -type d )) ; do \
		echo "checking subdir $$i" ; \
		if [ ! -L "$$i/buildsystem" ] ; then \
			echo "buildsystem symlink to ../../../../buildsystem is missing in $(shell pwd)/$$i You are using your own custom buildsystem." ; \
		echo "exit 706" ; \
			exit 1 ; \
		fi ; \
		if [ ! -L "$$i/Makefile" ] ; then \
			echo "Makefile symlink to ../../../../buildsystem/shared/u-boot-board-level.makefile is missing in $(shell pwd)/$$i You are using your own custom Makefile." ; \
		echo "exit 701" ; \
			exit 1 ; \
		fi ; \
		$(MAKE) -C $$i $* || exit 1 ; \
	done

# ------------------------------------------------------------------------------
#
# Target that prints the help
#
help :
	@echo "The target given to make will be called recursively on each board folder."
