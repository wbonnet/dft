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

# Build system sould be available under board folder as a symlink. Keep it
# locally available under board folder computing a relative path is a nightmare
# and does not work in all cases. Environment variables are not git friendly
# since git add will loose variable name and generate an absolute path, which
# is not comptible with user need ans or workspace relocation nor packagng needs.
# better solutions wille be really welcomeds contributions.
DFT_BUILDSYSTEM := ../buildsystem
include $(DFT_BUILDSYSTEM)/inc/lib.mk

# Do not recurse the following subdirs
MAKE_FILTERS  := Makefile README.md .

# ------------------------------------------------------------------------------
#
# Targets not associated with a file (aka PHONY)
#
.PHONY: help sanity-check

# Create a role entry
new-role:
	@echo "DEBUG : in ansible-roles.makefile running new-role with argument role-name $(role-name)" ; \
	if [ -z "$(role-name)" ] ; then \
		echo "DEBUG : from ansible-roles.makefile argument role-name is missing or has no value. Doing nothing..." ; \
		$(call dft_error ,2004-1701) ; \
	else  \
		if [ -d "./$(role-name)" ] ; then \
			echo ". Role $(role-name) already exist. Doing nothing..." ; \
		else  \
			echo ". Creating the directory for role $(role-name)" ; \
			cp -fr $(DFT_BUILDSYSTEM)/templates/ansible-role.template $(role-name)/ ; \
			sed -i -e "s/__ROLENAME__/$(role-name)/g" $(role-name)/README.md ; \
		fi ; \
	fi ;

# Simple forwarder
sanity-check:
	@for i in $(CHECK_FOR_SANITY) ; do \
		if [ -f ${CURDIR}/$$i/Makefile ] ; then \
			$(MAKE) -C $$i $@ ; \
		fi ; \
	done

# ------------------------------------------------------------------------------
#
# Target that prints the help
#
help:
	@echo "Available targets are :"
	@echo "   new-role                role-name=new_role_name"
	@echo "                           Initialize a new role entry (not added to git) with content of"
	@echo "                           $(DFT_BUILDSYSTEM)/templates/ansible-role.template"
	@echo "                           You will have to edit the generated files according to you role needs"
	@echo "   help                    Display this help"
