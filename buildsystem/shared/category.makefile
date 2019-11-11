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
CATEGORIES    = laptop desktop set-top-box single-board-computer

# ------------------------------------------------------------------------------
#
# Targets not associated with a file (aka PHONY)
#
.PHONY: help

#check que tes subdirs de category ont la et ont un lien makefile valide ensuite ca recurse
check :
	@echo "WARNING CATEGORY MAKEFILE PLACEHOLDER" ;
	# Board category directory must contain XXXboard.mk file, kernel folder and u-boot folder
	# Mandatory folders content check (otherwise recusive targets may not work)
	for i in $(filter-out $(MAKE_FILTERS),$(shell find . -maxdepth 1 -type d )) ; do \
		if [ ! -e "$$i/Makefile" ] ; then \
			echo "Makefile in $(shell pwd)/$$i is Missing. It should be a symlink to  ../../../buildsystem/shared/board.makefile" ; \
			echo "You can fix with the following shell commands :" ; \
			echo "ln -s ../../../buildsystem/shared/u-boot.makefile $$i/Makefile" ; \
			echo "git add $$i/Makefile" ; \
			echo "exit 101101" ; \
			exit 1 ; \
		fi ; \
		cd $$i ; \
		pwd ; \
		zelink=$(readlink Makefile) ; \
		echo "zelink : $$zelink" ; \
		if [ !  "readlink Makefile" = "../../../buildsystem/shared/board.makefile" ] ; then \
			echo "Makefile symlink in $$i must link to ../../../buildsystem/shared/board.makefile" ; \
			echo "ls -l $$i ../../../buildsystem/shared/board.makefile" ; \
			echo "It targets to `readlink $$i/Makefile`" ; \
			echo "exit 825" ; \
			exit 1 ; \
		else  \
			echo "le symlink est bon suis dans le else du if shell readlink donc = est vrai" ; \
		fi ; \
		cd .. ; \
	done ; \


# Catch all target. Call the same targets in each subfolder
%:
	@for i in $(filter-out $(MAKE_FILTERS),$(shell find . -maxdepth 1 -type d )) ; do \
		$(MAKE) -C $$i $* || exit 1 ; \
	done

# ------------------------------------------------------------------------------
#
# Target that prints the help
#
help :
	@echo "The target given to make will be called recursively on each board folder."
