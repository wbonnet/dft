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
# Defines the set of variables used for the u-boot.org project
#
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
#
# Defines the default values for directories
#
# WORK_DIR is the root of the workspace used to build the target software
# including all steps such as downloading, configuring, compiling, packaging, 
# etc.
#
# This folder contains either temporary, or volatile, subfolders (such as 
# package, extract) that can be rebuild from upstream sources even if it can 
# take some extra long long time, or version/board specific files under git 
# source control.
#
# The following items are under source control :
#  . Makefile (by default it is a symlink to a generic shared makefile)
#  . patches folder which contains local patches to apply on sources after 
#    extract stage. Patches file have to be listed in the Makefile (it 
#    can be a nice feature to add).
#  . files folder contains files needed to compile and produce package which
#    are not provided with upstream sources
#
# The following items are not under source control (and should not be) thus 
# they will be removed and destroyed by make mrproper :
#  . 'sources' folder and its subfolders (since sources are downloaded from
#    upstream and not kept in DFT git repository).
#  . 'workdir' and its subfolders
#
# -----------------------------------------------------------------------------

# Defines the work root (subfolders are persistent but workdir is destroyed)
BASE_DIR            ?= $(CURDIR)
WORK_DIR            ?= $(BASE_DIR)/workdir
FILE_DIR            ?= $(BASE_DIR)/files
PATCH_DIR           ?= $(BASE_DIR)/patches

# Defines the working dir subfolders (all are volatile)
SRC_DIR             ?= $(WORK_DIR)/sources/$(SRC_NAME)-$(SW_VERSION)
DOWNLOAD_DIR        ?= $(WORK_DIR)/download
GIT_DIR             ?= $(WORK_DIR)/git
PARTIAL_DIR         ?= $(DOWNLOAD_DIR)/partial
# TODO: should I keep BOARDNAME somewhere in the path
# COOKIE_DIR          ?= $(WORK_DIR)/cookies-$(BOARD_NAME)
COOKIE_DIR          ?= $(WORK_DIR)/cookies
INSTALL_DIR         ?= $(WORK_DIR)/install
PACKAGE_DIR         ?= $(WORK_DIR)/package
CHECKSUM_FILE       ?= $(WORK_DIR)/checksums
LOG_DIR             ?= $(WORK_DIR)/logs
# if not overriden the temporary files will go to /tmp
TEMP_DIR            ?= /tmp

# Defines the default targets used for building
CONFIGURE_SCRIPTS   ?= $(WORK_DIR)/configure
BUILD_SCRIPTS       ?= $(WORK_DIR)/Makefile

# ------------------------------------------------------------------------------
#
# Defines the default values for build environment and makefiles
#
# ------------------------------------------------------------------------------

# Defines board name
BOARD_NAME          ?= default-board

# If the KERNEL_DEFCONFIG variale is set, the given file will be copied to
# .config in the source dirctory. Default value is set to board name.
KERNEL_DEFCONFIG     ?= $(BOARD_NAME).config

# XXXX TODO If this variable is set, and USE_CONFIG_FILE is undefined, a config file will
# be generated using the given target. Default is to define nothing and let the
# user set one of the two choice, or run make by himself.
UBOOT_DEFCONFIG       ?=

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
ARCH_ARMV7L_BUILD_FLAGS   ?=

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

