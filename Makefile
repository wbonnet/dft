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
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#

# Build system sould be available from the root of git clone.
DFT_BUILDSYSTEM := ./buildsystem

# Do not recurse the following subdirs
MAKE_FILTERS  = Makefile README.md .

# Definition of the folders to check for sanity
CHECK_FOR_SANITY    = ansible-roles bsp-packages board-images

# ------------------------------------------------------------------------------
#
# Targets not associated with a file (aka PHONY)
#
.PHONY: help sanity-check

# Simple forwarder
sanity-check:
	@for i in $(CHECK_FOR_SANITY) ; do \
		if [ -f ${CURDIR}/$$i/Makefile ] ; then \
			$(MAKE) -C $$i $@ ; \
		fi ; \
	done

# Forward list-boards to bsp-packages folder
list-boards:
		@$(MAKE) -C bsp-packages $@ arch=$(arch) category=$(category); \

# ------------------------------------------------------------------------------
#
# Target that prints the help
#
help:
	@echo "Available targets are :"
	@echo "   sanity-check            Check the availability of required items (files, symlinks, directories)"
	@echo "                           In the following subdirs $(CHECK_FOR_SANITY)."
	@echo "                           This target only warns you and do not make any change to the tree content."
	@echo "   list-boards             Display the list of supported boards. Available filters are"
	@echo "                              arch=      (supported values are return values of command uname --machine)"
	@echo "                              category=  (desktop laptop phone set-top-box single-board-computer tablet)"
	@echo "   help                    Display this help"
