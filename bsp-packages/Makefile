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
	@echo "te faut l include de la liste des error codes et la fonction dft-error" ;
	@echo "te faut recuprer le bout de code qui fait le readlink dans une var" ;
	# Board level directory must contain board.mk file, kernel folder and u-boot folder
	# Mandatory folders content check (otherwise recusive targets may not work)
	@for i in $(CATEGORIES) ; do \
		if [ ! -d $$i ] ; then \
		echo "Warning : $$i category folder is missing, recursive targets may fail or produce incomplete set of binaries." ; \
		fi ; \
		if [ ! -e "$$i/Makefile" ] ; then \
			echo "Makefile in $(shell pwd)/$$i is Missing. It should be a symlink to  ../../buildsystem/shared/u-boot-board.makefile" ; \
			echo "You can fix with the following shell commands :" ; \
			echo "ln -s ../../buildsystem/shared/category.makefile $$i/Makefile" ; \
			echo "git add $$i/Makefile" ; \
			echo "exit 101101" ; \
			exit 1 ; \
		fi ; \
		if [ ! $(shell readlink $$i/Makefile) = "../../buildsystem/shared/u-boot-board.makefile" ] ; then \
			echo "iTODOMakefile symlink in $(shell pwd)/$$i must link to ../../buildsystem/shared/u-boot-board.makefile" ; \
			echo "It targets to $(shell readlink $i/Makefile)" ; \
			echo "exit 825" ; \
			exit 1 ; \
		fi ; \
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
