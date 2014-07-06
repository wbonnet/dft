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


# ------------------------------------------------------------------------------
#
# Defines the set of variables used for GNU project softwares 
#
# ------------------------------------------------------------------------------

GNU_SITE     = http://ftp.gnu.org
GNU_GNUROOT  = $(GNU_SITE)/gnu
GNU_NGNUROOT = $(GNU_SITE)/non-gnu
GNU_MIRROR   = $(GNU_GNUROOT)/$(GNU_PROJECT)/
GNU_NMIRROR  = $(GNU_NGNUROOT)/$(GNU_PROJECT)/




# Defines the default values for directories
#BASEDIR ?= $(CURDIR)
#FILEDIR ?= files
#PATCHDIR ?= patches
#WORKROOTDIR ?= work
#WORKDIR ?= $(WORKROOTDIR)/build-$(THIS_ARCHITECTURE)
#DOWNLOADDIR ?= $(WORKROOTDIR)/download
#PARTIALDIR ?= $(DOWNLOADDIR)/partial
#COOKIEROOTDIR ?= $(WORKROOTDIR)/cookies-$(THIS_ARCHITECTURE)
#COOKIEDIR ?= $(COOKIEROOTDIR)
#EXTRACTDIR ?= $(WORKDIR)
#WORKSRC ?= $(WORKDIR)/$(SOFTWARE_DISTNAME)
#OBJDIR ?= $(WORKSRC)
#INSTALLDIR ?= $(WORKROOTDIR)/install-$(THIS_ARCHITECTURE)
#PKGDIR ?= $(WORKROOTDIR)/package
#SCRATCHDIR ?= tmp
#TMPDIR ?= $(WORKDIR)/tmp
#TMPDIR_FULLPATH ?= $(shell pwd)/$(TMPDIR)
#CHECKSUM_FILE ?= checksums
#MANIFEST_FILE ?= manifest
#LOGDIR ?= log

# Defines the default targets used for building
#CONFIGURE_SCRIPTS ?= $(WORKSRC)/configure
#BUILD_SCRIPTS     ?= $(WORKSRC)/Makefile

# prepend the local file listing
#FILE_SITES = $(foreach DIR,$(FILEDIR) $(GARCHIVEPATH),file://$(DIR)/)

# Definition of the package that must be installed on each build platform
#PREREQUISITE_BASE_PKGS ?= make
#PREREQUISITE_BASE_PKGS_UBUNTU ?= build-essential
