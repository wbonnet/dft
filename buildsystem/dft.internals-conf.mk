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
$(info included dft.internals-conf.mk)
ifdef DFT_INTERNALS_CONF
$(error dft.internals-conf.mk has already been included)
else
define DFT_INTERNALS_CONF
endef
# the matching endif teminates this file
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

SRC_GIT_URL      ?= git://git.kernel.org/pub/scm/linux/kernel/git/stable
SRC_GIT_BRANCH   ?= stable
SRC_GIT_REPO     ?= linux-$(SRC_GIT_BRANCH)
SRC_GIT_REPO_EXT ?= .git
SRC_SITE         ?= https://cdn.kernel.org/pub/linux/kernel
SRC_FILE_VERSION ?= $(SRC_VERSION)
SRC_SRC_URL      ?= $(SRC_SITE)/$(SRC_BRANCH)/linux-$(SRC_FILE_VERSION).tar.xz
SRC_BRANCH       ?= v$(shell echo $(SRC_FILE_VERSION) | head -c 1).x

# Defines the software name if not set
SRC_NAME            ?= linux

# Defines the files to retrieve
SRC_DIST_FILES      ?= $(SRC_NAME)-$(SRC_FILE_VERSION).tar.xz
SRC_SIGN_FILES      ?= $(SRC_NAME)-$(SRC_FILE_VERSION).tar.xz.sign

# Defines the source repository
SRC_UPSTREAM_SITES  ?= $(SRC_SITE)/$(SRC_BRANCH)


# ------------------------------------------------------------------------------
#
# Defines the default values for directories
#
# ------------------------------------------------------------------------------

BASE_DIR            ?= $(CURDIR)
FILE_DIR            ?= files
PATCH_DIR           ?= patches
ifeq ($(DFT_BUILDSYSTEM_WORKDIR),)
  WORK_ROOT_DIR     ?= work-$(BOARD_NAME)
else
  WORK_ROOT_DIR     ?= $(DFT_BUILDSYSTEM_WORKDIR)/work-$(BOARD_NAME)
endif
WORK_DIR            ?= $(WORK_ROOT_DIR)/build-$(BOARD_NAME)
DOWNLOAD_DIR        ?= $(WORK_ROOT_DIR)/download
GIT_EXTRACT_DIR     ?= $(WORK_ROOT_DIR)/git
PARTIAL_DIR         ?= $(DOWNLOAD_DIR)/partial
COOKIE_DIR          ?= $(WORK_ROOT_DIR)/cookies-$(BOARD_NAME)
EXTRACT_DIR         ?= $(WORK_DIR)
WORK_SRC            ?= $(WORK_DIR)/$(SRC_FULLNAME)
OBJ_DIR             ?= $(WORK_SRC)
INSTALL_DIR         ?= $(WORK_ROOT_DIR)/install-$(BOARD_NAME)
PACKAGE_DIR         ?= $(WORK_ROOT_DIR)/package-$(BOARD_NAME)
TEMP_DIR            ?= $(WORK_DIR)/tmp
CHECKSUM_FILE       ?= checksums
LOG_DIR             ?= log

# Defines the default targets used for building
CONFIGURE_SCRIPTS   ?= $(WORK_SRC)/configure
BUILD_SCRIPTS       ?= $(WORK_SRC)/Makefile

# ------------------------------------------------------------------------------
#
# Defines the default values for build environment and makefiles
#
# ------------------------------------------------------------------------------

# Defines board name
BOARD_NAME          ?= default-board

# If the USE_CONFIG_FILE variale is set, then the given file will be copied to
# .config in the uild dirctory. Default is to define nothing.
USE_CONFIG_FILE     ?= $(BOARD_NAME).config

# If this variable is set, and USE_CONFIG_FILE is undefined, a config file will
# be generated using the given target. Default is to define nothing and let the
# user set one of the two choice, or run make by himself.
USE_DEFCONFIG       ?=

# The config file can be modified once set in the build dir (either using a build
# defconfig or by copying our own config file) by applying modifications defined
# in the overrides files. This is useful to store only differences between
# configuration file privided by kernel, and the config file we want to use
CONFIG_OVERRIDES    ?=

# Defines build flags to use all available cpus when running make
BUILD_PROCESS_COUNT ?= -j$(shell grep -c ^processor /proc/cpuinfo)

# Defines default build arguments, depending on the board architectures
ARCH_COMMON_BUILD_ARGS ?= modules
ARCH_ARMV7L_BUILD_ARGS  ?= zImage dtbs

# Defines default build targets depending on the board architectures
ARCH_COMMON_BUILD_FLAGS   ?=
ARCH_ARMV7L_BUILD_FLAGS    ?=

# Defines default build arguments, depending on the board architectures
# ARCH_COMMON_INSTALL_ARGS ?=
# ARCH_ARMV7L_INSTALL_ARGS  ?= "zImage dtbs"

# Defines standard make targets
BUILD_FLAGS   ?= $(ARCH_COMMON_BUILD_FLAGS) $(ARCH_$(shell echo $(BOARD_ARCH) | tr a-z A-Z)_BUILD_FLAGS)
BUILD_ARGS    ?= $(ARCH_COMMON_BUILD_ARGS) $(ARCH_$(shell echo $(BOARD_ARCH) | tr a-z A-Z)_BUILD_ARGS)

# Defines default installation arguments, depending on the board architectures
ARCH_COMMON_INSTALL_ARGS ?=
ARCH_ARMV7L_INSTALL_ARGS  ?= zinstall
ARCH_X86_64_INSTALL_ARGS  ?= zinstall
ARCH_I386_INSTALL_ARGS  ?= zinstall

INSTALL_ARGS    ?= $(ARCH_COMMON_INSTALL_ARGS) $(ARCH_$(shell echo $(BOARD_ARCH) | tr a-z A-Z)_INSTALL_ARGS)

# debuild configuration
DEBUILD        = debuild
DEBUILD_ARGS   = -us -uc
DEBUILD_ENV    = DEBUILD_TGZ_CHECK=no

# ------------------------------------------------------------------------------
# Match initial ifdef
endif

