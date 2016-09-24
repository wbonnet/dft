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
# Contributors list :
#
#    William Bonnet 	wllmbnnt@gmail.com
#
#


# ------------------------------------------------------------------------------
#
# Execute the configure script
#

configure-%/configure :
	@if test -f $(COOKIE_DIR)/configure-$*/configure ; then \
		true ; \
	else \
		echo "    running configure in $(OBJ_DIR)" ; \
		cd "$(OBJ_DIR)" && $(CONFIGURE_ENV) $(abspath $*)/configure $(CONFIGURE_ARGS) ; \
	fi ; 
	$(TARGET_DONE)

reconfigure-%/configure :
	@if test -f $(COOKIE_DIR)/configure-$*/configure ; then \
		rm -f $(COOKIE_DIR)/configure-$*/configure ; \
	fi ; 
	$(TARGET_DONE)

