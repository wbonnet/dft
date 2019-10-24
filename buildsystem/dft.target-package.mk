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
# Protection against multiple includes
#
$(info included dft.target-package.mk)
ifdef DFT_BUILDSYSTEM_TARGET_PACKAGE
$(error dft.target-package.mk has already been included)
else
define DFT_BUILDSYSTEM_TARGET_PACKAGE
endef
# the matching endif teminates this file

# ------------------------------------------------------------------------------
#
# Execute the package target script
#

do-package :
	if test -f $(COOKIE_DIR)/do-package ; then \
		true ; \
	else \
		echo "        running package in $(PACKAGE_DIR)"  ; \
		cd $(PACKAGE_DIR) ; \
		if [ "$(SRC_NAME)" = "linux" ] ; then \
			mkdir -p $(SRC_NAME)-kernel-$(BOARD_NAME) ; \
			cd $(SRC_NAME)-kernel-$(BOARD_NAME) ; \
		else \
			mkdir -p $(SRC_NAME)-$(BOARD_NAME) ; \
			cd $(SRC_NAME)-$(BOARD_NAME) ; \
		fi ; \
		[ -f debian ] && rm -f debian ; \
		echo " DEBUG PLOP 1 avant le cp -fr basedir/debian vers debian SUIS LA VIRE MOI        running package in $(PACKAGE_DIR)"  ; \
		cp -fr $(BASE_DIR)/debian debian ; \
		echo " DEBUG PLOP 2 avant le cp -fr install_dir etoile SUIS LA VIRE MOI        running package in $(PACKAGE_DIR)"  ; \
		cp -fr $(INSTALL_DIR)/* . ; \
		echo " DEBUG PLOP 3 avant le tar SUIS LA VIRE MOI"  ; \
		echo "tar cvfz ../$(SRC_NAME)-$(BOARD_NAME)_$(SW_VERSION).orig.tar.gz * " ; \
		if [ "$(SRC_NAME)" = "linux" ] ; then \
			tar cvfz ../$(SRC_NAME)-kernel-$(BOARD_NAME)_$(SW_VERSION).orig.tar.gz * ; \
		else \
			tar cvfz ../$(SRC_NAME)-$(BOARD_NAME)_$(SW_VERSION).orig.tar.gz * ; \
		fi ; \
		echo " DEBUG PLOP 4 avant le debuild SUIS LA VIRE MOI"  ; \
		echo " DEBUG PLOP 5 le pwd"  ; \
		pwd ; \
		echo " DEBUG PLOP 6 les fichiers par ls -lh"  ; \
		ls -lh ; \
		echo " DEBUG PLOP 7 les fichiers par ls -lh .."  ; \
		ls -lh .. ; \
		$(DEBUILD_ENV) $(DEBUILD) $(DEBUILD_ARGS) ; \
		echo " DEBUG PLOP 8 apres le debuild SUIS LA VIRE MOI"  ; \
	fi ; \
	$(TARGET_DONE)

do-repackage :
	@if test -f $(COOKIE_DIR)/do-package ; then \
		rm -f $(COOKIE_DIR)/do-package ; \
		rm -fr $(abspath $(PACAKGE_DIR)) ; \
	fi ;
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
#
# Create the Debian package
#

package : install $(PACKAGE_DIR) pre-package do-package post-package
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)


# ------------------------------------------------------------------------------
#
# Execute once again the package target
#

repackage : install pre-repackage do-repackage package post-repackage
	$(DISPLAY_COMPLETED_TARGET_NAME)
	$(TARGET_DONE)

# ------------------------------------------------------------------------------
# Match initial ifdef
endif

