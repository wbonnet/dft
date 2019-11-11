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
.PHONY: help check


# Catch all target. Call the same targets in each subfolder
%:
	echo 'target generique' ; \
	@for i in $(filter-out $(MAKE_FILTERS),$(shell find . -maxdepth 1 -type d )) ; do \
		$(MAKE) -C $$i $* || exit 1 ; \
	done

# This target checks that all mandatorry items are prent and symlinks are valid, then recurse check
check:
	echo 'target check' ; \
	@for i in $(filter-out $(MAKE_FILTERS),$(shell find . -maxdepth 1 -type d )) ; do \
		if [ ! -e $$i/Makefile ] ; then \
			echo "Makefile symlink in $(shell pwd)/$$i is missing, it should link to ../../buildsystem/shared/u-boot-board.makefile" ; \
			echo "You can fix with the following commands : " ; \
			echo "ln -s ../../../buildsystem/shared/u-boot-board.makefile $$i/Makefile " ; \
			echo "git add $$i/Makefile" ; \
			echo "exit 826" ; \
			exit 1 ; \
		fi ; \
		if [ ! $(shell readlink $$i/Makefile) = "../../buildsystem/shared/u-boot-board.makefile" ] ; then \
			echo "Makefile symlink in $(shell pwd)/$$i must link to ../../buildsystem/shared/u-boot-board.makefile" ; \
			echo "It targets to $(shell readlink $i/Makefile)" ; \
			echo "exit 825" ; \
			exit 1 ; \
		fi ; \
	done ; \
	echo "check loop on Makefile symlinks in board subdirs successfull"; \
	echo "starting to call recursive check target in board subdirs"; \
	for i in $(filter-out $(MAKE_FILTERS),$(shell find . -maxdepth 1 -type d )) ; do \
		echo "uboot-boardkind.makefile second for"; \
		pwd ; \
		if [ ! "$(shell readlink Makefile)" = "../../../buildsystem/shared/u-boot-board.makefile" ] ; then \
			echo "Makefile symlink in $(shell pwd)/$$i must link to ../../../buildsystem/shared/u-boot-board.makefile" ; \
			echo "exit 821" ; \
			exit 1 ; \
		fi ; \
		cd $$i ; \
		if [ ! "$(shell readlink ./Makefile)" = "../../../buildsystem/shared/u-boot-board.makefile" ] ; then \
			echo "Makefile symlink in $(shell pwd)/$$i must link to ../../../buildsystem/shared/u-boot-board.makefile" ; \
			echo "exit 822" ; \
			exit 1 ; \
		fi ; \
		if [ ! -d "u-boot" ] ; then \
			echo "u-boot directory is missing in $(shell pwd)/$$i" ; \
			echo "exit 823" ; \
			exit 1 ; \
		fi ; \
		if [ ! -d "kernel" ] ; then \
			echo "kernel directory is missing in $(shell pwd)/$$i" ; \
			echo "exit 824" ; \
			exit 1 ; \
		fi ; \
		if [ ! -L "Makefile" ] ; then \
			echo "Makefile symlink to ../../../buildsystem/shared/u-boot-board.makefile is missing in $(shell pwd)" ; \
			echo "You can fix with the following commands : " ; \
			echo "ln -s ../../../buildsystem/shared/u-boot-board.makefile $$i/Makefile " ; \
			echo "git add $$i/Makefile" ; \
			echo "exit 783" ; \
			exit 1 ; \
		fi ; \
	 	diff ./Makefile "../../../../buildsystem/shared/u-boot-board.makefile" || echo "premier diffexit 789" ; \
	 	diff ./Makefile "../../../../buildsystem/shared/u-boot-board.makefile" || exit 1 ; \
		if [  "${Makefile_symlink}" = "../../../buildsystem/shared/u-boot-board.makefile" ] ; then \
			echo "Target of symlink Makefile should be ../../../buildsystem/shared/u-boot-board.makefile in directory $(shell pwd)/$$i" ; \
			echo "Error since it is " ; readlink ./Makefile ; \
			echo "You can fix with the following commands : " ; \
			echo "ln -s ../../../buildsystem/shared/u-boot-boardkind-level.makefile $$i/Makefile" ; \
			echo "git add $$i/Makefile " ; \
			echo "exit second 789" ; \
			exit 1 ; \
		fi ; \
		cd .. ; \
		$(MAKE) -C $$i $* || exit 1 ; \
	done

# ------------------------------------------------------------------------------
#
# Target that prints the help
#
help:
	@echo "The target given to make will be called recursively on each board folder."
