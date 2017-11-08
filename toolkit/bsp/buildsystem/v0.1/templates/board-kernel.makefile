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
		echo ". Creating the directory structure (./$(NEW_VERSION))" ; \
		mkdir -p $(NEW_VERSION) ; \
		cp -f ../../buildsystem/current/templates/kernel-version.makefile $(NEW_VERSION)/Makefile ; \
		ln -s ../../../buildsystem/current $(NEW_VERSION)/buildsystem ; \
		mkdir -p $(NEW_VERSION)/files ; \
		touch $(NEW_VERSION)/files/.gitkeep ; \
		mkdir -p $(NEW_VERSION)/patches ; \
		touch $(NEW_VERSION)/patches/.gitkeep ; \
		sed -i -e "s/__KERNEL_VERSION__/$(NEW_VERSION)/g" $(NEW_VERSION)/Makefile ; \
		git add $(NEW_VERSION) ; \
	fi ; 

# Catch all target. Call the same targets in each subfolder
%:
	@for i in $(filter-out $(FILTER_DIRS),$(wildcard */)) ; do \
		$(MAKE) -C $$i $* || exit 1 ; \
	done
