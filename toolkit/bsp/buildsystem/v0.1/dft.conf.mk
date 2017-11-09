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
# Retrieves informations about the host used to build the softwares
#
# ------------------------------------------------------------------------------

BUILDER_HOSTNAME                 := $(shell uname -n)
BUILDER_ARCHITECTURE             := $(shell uname -s | tr '[:upper:]' '[:lower:]')-$(shell uname -m | tr '[:upper:]' '[:lower:]')
BUILDER_OPERATING_SYSTEM         := $(shell uname -s | tr '[:upper:]' '[:lower:]')
BUILDER_OPERATING_SYSTEM_FLAVOR  := $(word 3, $(shell lsb_release -i | tr '[:lower:]' '[:upper:]'))
BUILDER_OPERATING_SYSTEM_VERSION := $(word 2, $(shell lsb_release -c | tr '[:lower:]' '[:upper:]'))


# ------------------------------------------------------------------------------
#
# Defines the set of variables used for the Kernel.org project
#
# ------------------------------------------------------------------------------

KERNEL_SITE     = https://cdn.kernel.org/pub/linux/kernel
KERNEL_SRC_URL  = $(KERNEL_SITE)/$(KERNEL_BRANCH)/linux-$(KERNEL_VERSION).tar.xz
KERNEL_BRANCH   = v$(shell echo $(KERNEL_VERSION) | head -c 1).x

# Defines the software name if not set
SOFTWARE_UPSTREAM_NAME = linux

# Defines the files to retrieve
SOFTWARE_DIST_FILES     ?= $(SOFTWARE_UPSTREAM_NAME)-$(KERNEL_VERSION).tar.xz
SOFTWARE_SIGN_FILES     ?= $(SOFTWARE_UPSTREAM_NAME)-$(KERNEL_VERSION).tar.xz.sign

# Defines the source repository
SOFTWARE_UPSTREAM_SITES ?= $(KERNEL_SITE)/$(KERNEL_BRANCH)


# ------------------------------------------------------------------------------
#
# Defines the default values for directories
#
# ------------------------------------------------------------------------------

BASE_DIR            ?= $(CURDIR)
FILE_DIR            ?= files
PATCH_DIR           ?= patches
WORK_ROOT_DIR       ?= work
WORK_DIR            ?= $(WORK_ROOT_DIR)/build-$(BUILDER_ARCHITECTURE)
DOWNLOAD_DIR        ?= $(WORK_ROOT_DIR)/download
PARTIAL_DIR         ?= $(DOWNLOAD_DIR)/partial
COOKIE_DIR          ?= $(WORK_ROOT_DIR)/cookies-$(BUILDER_ARCHITECTURE)
EXTRACT_DIR         ?= $(WORK_DIR)
WORK_SRC            ?= $(WORK_DIR)/$(SOFTWARE_FULLNAME)
OBJ_DIR             ?= $(WORK_SRC)
INSTALL_DIR         ?= $(WORK_ROOT_DIR)/install-$(BUILDER_ARCHITECTURE)
TEMP_DIR            ?= $(WORK_DIR)/tmp
CHECKSUM_FILE       ?= checksums
LOG_DIR             ?= log

# Defines the default targets used for building
CONFIGURE_SCRIPTS   ?= $(WORK_SRC)/configure
BUILD_SCRIPTS       ?= $(WORK_SRC)/Makefile
