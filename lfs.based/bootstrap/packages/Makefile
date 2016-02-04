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
#
# Copyright 2014 LFFS project (http://www.linuxfirmwarefromscratch.org).  
# All rights reserved. Use is subject to license terms.
#
# Even if this work is a complete rewrite, it is originally derivated work based 
# upon mGAR build system from OpenCSW project (http://www.opencsw.org).
#
# Copyright 2001 Nick Moffitt: GAR ports system
# Copyright 2006 Cory Omand: Scripts and add-on make modules, except where otherwise noted.
# Copyright 2008 Dagobert Michelsen (OpenCSW): Enhancements to the CSW GAR system
# Copyright 2008-2013 Open Community Software Association: Packaging content
#
#
#
# Contributors list :
#
#    William Bonnet 	wllmbnnt@gmail.com
#
#

# Store the software name
NEW_SOFTWARE_NAME    = $*

# Create a new software version entry in the repository
new-software-%:
    # Create the directory that will contains the new software
	@mkdir -p $(NEW_SOFTWARE_NAME)

    # Create the directory that will contains patches on the new software
	@mkdir -p $(NEW_SOFTWARE_NAME)/patches

    # Create the directory that will contains specific files for the new software
	@mkdir -p $(NEW_SOFTWARE_NAME)/files

    # Copy the Makefile template to the new software directory
	@cp -f ../../buildsystem/current/templates/software.makefile $(NEW_SOFTWARE_NAME)/Makefile

    # Create a link to the generic software.mk. Link should be removed and a file created
    # in case of specific need for the given software
	@(cd $(NEW_SOFTWARE_NAME) && ln -s ../software.mk $(NEW_SOFTWARE_NAME).mk && cd ..)

    # Switch to the software directory and create a link to the build system
	@(cd $(NEW_SOFTWARE_NAME) && ln -s ../../../buildsystem/current buildsystem && cd ..)

    # Set the software name in the new software Makefile
	@(sed -i -e "s/%%SOFTWARE_UPSTREAM_NAME%%/$(NEW_SOFTWARE_NAME)/g" $(NEW_SOFTWARE_NAME)/Makefile )

    # Last step is to add the new directory to GIT
	@git add $(NEW_SOFTWARE_NAME)


# Catch all target. Call the same targets in each subfolder
%:
	@for i in $(filter-out $(FILTER_DIRS),$(wildcard */)) ; do \
		$(MAKE) -C $$i $*  || exit 1 ; \
	done
