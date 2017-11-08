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
# Copyright 2016 DFT project (http://www.debianfirmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#

# Defines the software version
NEW_VERSION = $*

# Create a new boar entry in the repository
new-version-%:
	@if [ -d "./$(NEW_VERSION)" ] ; then \
		echo ". Directory ./($(NEW_VERSION) already exist. Doing nothing..." ; \
	else  \
		echo ". Creating the directory storing the kernerl sources for given version (./$(NEW_VERSION))" ; \
		mkdir -p $(NEW_VERSION) ; \
		echo ". Copying the Makefile template to the new version directory" ; \
		cp -f ../../buildsystem/current/templates/uboot-version.makefile $(NEW_VERSION)/Makefile ; \
		echo ". Adding ./$(NEW_VERSION) to git" ; \
		git add $(NEW_VERSION) ; \
	fi ; 

# Catch all target. Call the same targets in each subfolder
%:
	@for i in $(filter-out $(FILTER_DIRS),$(wildcard */)) ; do \
		$(MAKE) -C $$i $* || exit 1 ; \
	done
