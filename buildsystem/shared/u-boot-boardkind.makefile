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
MAKE_FILTERS  = Makefile README.md .

# ------------------------------------------------------------------------------
#
# Targets not associated with a file (aka PHONY)
#
.PHONY: help

# Catch all target. Call the same targets in each subfolder
%:
	@for i in $(filter-out $(MAKE_FILTERS),$(shell find . -maxdepth 1 -type d )) ; do \
		$(MAKE) -C $$i $* || exit 1 ; \
	done

check:
	for i in $(filter-out $(MAKE_FILTERS),$(shell find . -maxdepth 1 -type d )) ; do \
		cd $$i ; \
		if [ ! -L "$$i/Makefile" ] ; then \
			echo "Makefile symlink to ../../../../buildsystem/shared/u-boot-boardkind-level.makefile is missing in $(shell pwd)/$$i" ; \
			echo "You can fix with the following commands : " ; \
			echo "ln -s ../../../buildsystem/shared/u-boot-boardkind-level.makefile $$i/Makefile " ; \
			echo "git add $$i/Makefile" ; \
			echo "exit 783" ; \
			exit 1 ; \
		fi ; \
		if [ ! "$(shell readlink $$i/Makefile)" = "../../../buildsystem/shared/u-boot-boardkind-level.makefile" ] ; then \
			echo "Target of symlink Makefile should be ../../../buildsystem/shared/u-boot-boardkind-level.makefile in directory $(shell pwd) You are using your own custom buildsystem." ; \
			echo "You can fix with the following commands : " ; \
			echo "ln -s ../../../buildsystem/shared/u-boot-boardkind-level.makefile $$i/Makefile " ; \
			echo "git add $$i/Makefile " ; \
			echo "exit 789" ; \
			exit 1 ; \
		fi ; \
		$(MAKE) -C $$i $* || exit 1 ; \
		cd .. ; \
	done

# ------------------------------------------------------------------------------
#
# Target that prints the help
#
help :
	@echo "The target given to make will be called recursively on each board folder."
