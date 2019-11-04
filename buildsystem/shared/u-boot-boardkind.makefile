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

# TODO: FIXME: ugly solution until i know how to write a correct readlink comparison in if embeded bash" \
check:
	for i in $(filter-out $(MAKE_FILTERS),$(shell find . -maxdepth 1 -type d )) ; do \
		pwd ; \
		echo "now checking $$i"; \
		cd $$i ; \
		echo "cd done" ; \
		pwd ; \
		ls -l ; \
		if [ ! -L "Makefile" ] ; then \
			echo "Makefile symlink to ../../../buildsystem/shared/u-boot-board.makefile is missing in $(shell pwd)/$$i" ; \
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
		echo "after cd .. now in $(shell pwd)" ; \
		$(MAKE) -C $$i $* || exit 1 ; \
	done

# ------------------------------------------------------------------------------
#
# Target that prints the help
#
help :
	@echo "The target given to make will be called recursively on each board folder."
