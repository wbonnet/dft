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
$(info included dft.kernel.mk)
ifdef DFT_BUILDSYSTEM_KERNEL
# the matching endif teminates this file
$(error dft.kernel.mk has already been included)
else
define DFT_BUILDSYSTEM_KERNEL
endef

# ------------------------------------------------------------------------------
#
# Defines the set of variables used for the kernel.org project
#
# ------------------------------------------------------------------------------

SRC_GIT_URL         ?= git://git.kernel.org/pub/scm/linux/kernel/git/stable
SRC_GIT_BRANCH      ?= stable
SRC_GIT_REPO        ?= linux-$(SRC_GIT_BRANCH)
SRC_GIT_REPO_EXT    ?= .git
SRC_SITE            = https://cdn.kernel.org/pub/linux/kernel
SRC_FILE_VERSION    ?= $(SW_VERSION)
SRC_DIST_URL        ?= $(SRC_SITE)/$(SRC_BRANCH)
SRC_BRANCH          ?= v$(shell echo $(SRC_FILE_VERSION) | head -c 1).x

# Defines the files to retrieve
SRC_DIST_FILES      ?= $(SRC_NAME)-$(SW_VERSION).tar.xz
SRC_SIGN_FILES      ?= $(SRC_NAME)-$(SW_VERSION).tar.xz.sign

# ------------------------------------------------------------------------------
#
# Overrides some definition to compile uboot using the same makefiles
#

# Defines the git repository to use
DOWNLOAD_TOOL    = wget
SRC_NAME         = linux
BUILD_ARGS       =

include buildsystem/dft.mk

# ------------------------------------------------------------------------------
# Match initial ifdef
endif
