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
# Copyright 2017 DFT project (http://www.debianfirmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
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
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#


# ------------------------------------------------------------------------------
#
# Execute the configure script
#
# TODO : DELTA DEFCONFIG
configure-%/configure :
	@if test -f $(COOKIE_DIR)/configure-$*/configure ; then \
		true ; \
	else \
		if [ "$(USE_CONFIG_FILE)" != "" ] ; then \
			echo "    copying $(USE_CONFIG_FILE) to .config" ; \
			cp -f $(FILE_DIR)/$(USE_CONFIG_FILE) $(OBJ_DIR)/.config ; \
		else \
			if [ "$(USE_DEFCONFIG)" != "" ] ; then \
				echo "    running make $(BUILD_FLAGS) $(USE_DEFCONFIG) in $(OBJ_DIR)" ; \
				cd "$(OBJ_DIR)" && make $(USE_DEFCONFIG) ; \
			else \
				echo "    running configure in $(OBJ_DIR)" ; \
				cd "$(OBJ_DIR)" && $(CONFIGURE_ENV) $(abspath $*)/configure $(CONFIGURE_ARGS) ; \
			fi ; \
		fi ; \
	fi ;
	$(TARGET_DONE)

reconfigure-%/configure :
	@if test -f $(COOKIE_DIR)/configure-$*/configure ; then \
		rm -f $(COOKIE_DIR)/configure-$*/configure ; \
	fi ;
	$(TARGET_DONE)

