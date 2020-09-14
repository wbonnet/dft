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
# Copyright 2017 DFT project (http://www.firmwaretoolkit.org).
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
# Protection against multiple include
#
ifdef DFT_UBOOT
$(info u-boot.mk has already been included)
else
#$(info now including u-boot.mk)
DFT_UBOOT = 1
# Some temporary default values used to debug where where variables are initialized
SW_NAME     := u-boot
SW_VERSION  ?= out-of-scope

# ------------------------------------------------------------------------------
#
# Defines the set of variables used for the u-boot.org project
#
# ------------------------------------------------------------------------------

SRC_GIT_URL         ?= "SRC_GIT_URL Not used -- git://git.kernel.org/pub/scm/linux/kernel/git/stable"
SRC_GIT_BRANCH      ?= "SRC_GIT_BRANCH Not Used -- stable"
SRC_GIT_REPO        ?= "SRC_GIT_REPO Not Used -- linux-$(SRC_GIT_BRANCH)"
SRC_GIT_REPO_EXT    ?= "SRC_GIT_REPO_EXT Not Used -- .git"
SRC_FILE_VERSION    ?= $(shell echo $(SW_VERSION) | head -c 1)
DFT_SRC_SITE        ?= https://github.com/
SRC_DIST_URL        ?= $(DFT_SRC_SITE)/$(SW_NAME)/$(SW_NAME)/archive
SW_LATEST           ?= $(shell find . -mindepth 1 -maxdepth 1 -type d -name "*\.*" | sort -r |  head -n 1 | cut -d \/ -f 2)

# Defines the files to retrieve
SRC_DIST_FILES      ?= v$(SW_VERSION).tar.gz
SRC_SIGN_FILES      ?= $(SW_NAME)-$(SW_VERSION).sign

# ------------------------------------------------------------------------------
#
# Overrides some definition to compile uboot using the same makefiles
#
# ------------------------------------------------------------------------------

# Defines the git repository to use
DOWNLOAD_TOOL       := wget
SW_NAME             := u-boot
BUILD_ARGS          =

# Match initial ifdef DFT_UBOOT
endif
