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
ifdef DFT_CONF
$(info conf.mk has already been included)
else
$(info now including conf.mk)
DFT_CONF = 1

# Some temporary default values used to debug where where variables are initialized
SW_NAME     ?= no-name-at-conf
SW_VERSION  ?= no-version-at-conf

# ------------------------------------------------------------------------------
#
# Retrieves informations about the host used to build the softwares
#
# ------------------------------------------------------------------------------

BUILDER_HOSTNAME                 := $(shell uname -n)
BUILDER_ARCH                     := $(shell uname -m | tr '[:upper:]' '[:lower:]')
BUILDER_OPERATING_SYSTEM         := $(shell uname -s | tr '[:upper:]' '[:lower:]')
BUILDER_OPERATING_SYSTEM_FLAVOR  := $(word 3, $(shell lsb_release -i | tr '[:lower:]' '[:upper:]'))
BUILDER_OPERATING_SYSTEM_VERSION := $(word 2, $(shell lsb_release -c | tr '[:lower:]' '[:upper:]'))

HOST_ARCH ?= $(shell uname -m)

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


# Defines the work root (subfolders are persistent but workdir is destroyed)A
# TODO remove all DFT_HOME after current debug sessions
# TODO remove all DFT_WORKSPACE after current debug sessions keep only WORKDIR ?
# reference to /fordidden are made to force failure of make an detect misuse
# of env vars. The /fobidden should have access flags 400 and belong to root.
# Keep It Stupid Simple KISS ;)

# DFT_HOME is the path to where DFT is installed. It should contain buildsystem
# folder storng all the Makefiles tool chain with and its .mk include files
DFT_HOME            = /usr/share/dft

# DFT_WORK is the root (highest level) of all work dirs used by DFT. Its
# content is considered as volatile even if it will store some git stuff. 
# It means it is "work dir" and if you changes and add to git folders are 
# important you have to commit / push the files to upstream github.
# Several context dependant wordirs will be created under this place 
# during makefiles execution and recursion (for kernels etc.).
#
# It is up to you to ensure there will be enough free space depending
# on how many targets you are building at a time. SSD or even ramdisk 
# can really speed up thing s but don't expect to build all versions for a
# board unles you have a few gigs of Ram :)
#
# If you build rootfs or firmware images the file system underneath DFT_WORK
# has to support 'mount bind ' in chrooted environnement, so be careful is 
# you use a NFS backend.
# If variable is not defined in the makefile variables then its value is
# retrieved from shell env. This means DFT_WORK value can be defined on the 
# command line using DFT_WORK=/path/to/somewhere make show-config
DFT_WORK ?= /tmp/dft-work

# DFT_BUILDSYSTEM is where the Mafile toolchain is installed. The following 
# value is computed from the current makefile location if it has not been 
# manually set. This is useful development purposes since all path are relative.
# In the packaged version relative path are still the same (meaning don't care 
# since it works out of the box), and this prevent you to add absolute path to 
# git repo since it would fail when trying to write to a rea only place (in 
# this use case fail fast approch is better).
DFT_BUILDSYSTEM     ?= $(dir $(lastword $(MAKEFILE_LIST)))

# DFT_WORKSPACE is where the current workdir should be located. It should be 
# under DFT_WORK and can be vorriden on the commande line used to run make for 
# instance to use a different place because of storage capacity or 
# performance  reasons.
DFT_WORKSPACE         ?= $(DFT_WORK)/dft-workspace

# DFT_WORK is the name of directory under DFT_WORKSPACE used to build a version 
# of a given pice of software (kernel, u-boot, etc.) or even a rootfs or firware
# bootable disk image.
WORK_DIR            ?= $(DFT_WORKSPACE)/$(BOARD_NAME)_$(SW_NAME)/$(SW_VERSION)

# Hint : All the variables with a name ending with DIR define a path located in the 
# context of the current board for a given software, then a given version of this 
# sofware. Hoping thus hint can help you understand the logic behind the naming convention
# 
# FILE_DIR contain all the static files nedeed by compilation of packaging steps
# Since files in this folder are supposed to be static this folder should be located under
# DFT_BUILDSYSTEM which is read-only for common use. DFT development like adding support
# for a new board or new u-boot or kernel versions require git ande write access anyways,
# thus git repo must be placed elsewhere than thedefault location which is /usr/share).
FILE_DIR            ?= $(WORK_DIR)/files

# DEFCONFIG_DIR contains the defconfig files used for kernel building. There
# is one file under git per kernel version of a given board (the board is defined
# by folder hierarchy).
DEFCONFIG_DIR       ?= $(WORK_DIR)/defconfig

# PATCH_DIR contain all the patches to be applied on upstream sources during
# make patch target execution.
PATCH_DIR           ?= $(WORK_DIR)/patches

# Definition of the work dir subfolders (all are also volatile)
BUILD_DIR           ?= $(WORK_DIR)/build
GIT_DIR             ?= $(WORK_DIR)/git
COOKIE_DIR          ?= $(WORK_DIR)/cookies
INSTALL_DIR         ?= $(WORK_DIR)/install
PACKAGE_DIR         ?= $(WORK_DIR)/package
CHECKSUM_FILE       ?= $(WORK_DIR)/checksums
LOG_DIR             ?= $(WORK_DIR)/logs
DOWNLOAD_DIR        ?= $(WORK_DIR)/download
PARTIAL_DIR         ?= $(DOWNLOAD_DIR)/partial
# if not overriden the temporary files will go to /tmp please check your env
# in case you store /tmp into ramdisk it can use a lot a RAM...
TEMP_DIR            ?= /tmp

# Defines the default targets used for building
CONFIGURE_SCRIPTS   ?= $(WORK_DIR)/configure
BUILD_SCRIPTS       ?= $(WORK_DIR)/Makefile

# ------------------------------------------------------------------------------
#
# Defines the default values for build environment and makefiles
#
# ------------------------------------------------------------------------------

# Default download tool is wget since it is used to retrieve most of source. git is available
# DOWNLOAD_TOOL should beset to git in custom makefiles if needed
DOWNLOAD_TOOL       := wget

# Default is to turn wget to quiet mode to hide progress bar in shell output 
WGET_OPTS           := -q

# Defines default values to undefined (to make simple retrieval with grep in logs...)
BOARD_NAME          ?= undefined-board-name
BOARD_ARCH          ?= undefined-board-arch
DEFAULT_DTB         ?= undefined-default.dtb

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
ARCH_ARMV7L_INSTALL_ARGS ?= zinstall
ARCH_X86_64_INSTALL_ARGS ?= zinstall
ARCH_I386_INSTALL_ARGS   ?= zinstall

INSTALL_ARGS    ?= $(ARCH_COMMON_INSTALL_ARGS) $(ARCH_$(shell echo $(BOARD_ARCH) | tr a-z A-Z)_INSTALL_ARGS)

# debuild configuration
DEBUILD        = debuild
DEBUILD_ARGS   = -us -uc
DEBUILD_ENV    = DEBUILD_TGZ_CHECK=no

# ------------------------------------------------------------------------------
# Match initial ifdef DFT_CONF
endif

