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
list-boards list-architectures :
		@$(MAKE) -C bsp-packages $@ arch=$(arch) category=$(category); \

# ------------------------------------------------------------------------------
#
# Target that prints the generic top level help
#
help:
	@echo "Inline help is allocated in several categories according to functionnal scope"
	@echo 
	@echo "Available targets to display scoped help are :"
	@echo " help-bsp                Help about BSP building targets"
	@echo " help-config-file        Help about configuration file"
	@echo " help-env-vars           Help about environnment variables"
	@echo " help-catalog            Help about catalog listing target (list of supported board, arch, versions)"
	@echo " help-images             Help about image building targets"
	@echo " help-examples           Help about examples building targets"
	@echo " help-sanity             Help about buildsystem sanity check targets"
	@echo " help                    Display this help"

# ------------------------------------------------------------------------------
#
# Help about images building targets
#
help-images:
	@echo "Available targets are :"

# ------------------------------------------------------------------------------
#
# Help about bsp building targets
#
help-bsp:
	@echo "Available targets are :"

# ------------------------------------------------------------------------------
#
# Help about configuration file
#
help-config-file:
	@echo "Available targets are :"

# ------------------------------------------------------------------------------
#
# Help about configuration file
#
help-env-vars:
	@echo "Available targets are :"

# ------------------------------------------------------------------------------
#
# Help about buildsystem sanity check targets
#
help-sanity:
	@echo "Available targets are :"
	@echo "    sanity-check           Check the availability of required items (files, symlinks, directories)"
	@echo "                           Recursivly in subdirs $(CHECK_FOR_SANITY)."
	@echo "                           This target only warns you and do not make any change to the tree content."

# ------------------------------------------------------------------------------
#
# Help about examples building targets
#
help-examples:
	@echo "Available targets are :"

# ------------------------------------------------------------------------------
#
# Help about targets handling catalog of supported items printing and querying
#
help-catalog:
	@echo "Catalog management functionalities. The following helper targets can be used to query"
	@echo "and modify the catalog (such as adding new boards or categories)"
	@echo
	@echo "Available targets are :"
	@echo "    list-boards             Display the list of supported boards (support filters)."
	@echo "    list-architectures      Display the list of supported CPU architectures (support filters)"
	@echo
	@echo "Available filters for the list targets are :"
	@echo "    arch=                   (supported values are return values of command uname --machine)"
	@echo "    category=               (desktop laptop phone set-top-box single-board-computer tablet)"
	@echo
	@echo "One or several filters can be passed to the make command to reduce the ouput of list-* targets"

