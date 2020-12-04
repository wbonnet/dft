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
# Copyright 2019 DFT project (http://www.firmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#

DFT_BUILDSYSTEM := ../buildsystem
include $(DFT_BUILDSYSTEM)/dft.mk

# Do not recurse the following subdirs
MAKE_FILTERS  = Makefile  linux-kernel-fragments README.md . sbit

# definition of the board categories to process
CATEGORIES    = laptop desktop devkit set-top-box single-board-computer phone tablet

# ------------------------------------------------------------------------------
#
# Targets not associated with a file (aka PHONY)
#
.PHONY: help sanity-check list-boards list-architectures show-u-boot-available-upgrade show-kernel-available-upgrade

# Build only u-boot package target
u-boot-package:
	for i in $(filter-out $(MAKE_FILTERS),$(shell find . -mindepth 1 -maxdepth 1 -type d )) ; do \
		if [ -f $$i/Makefile ] ; then \
			$(MAKE) --no-print-directory --directory=$$i u-boot-package; \
		fi ; \
	done

# Build only linux kernel an package target
linux-kernel-package:
kernel-package:
	@for i in $(filter-out $(MAKE_FILTERS),$(shell find . -mindepth 1 -maxdepth 1 -type d )) ; do \
		if [ -f $$i/Makefile ] ; then \
			$(MAKE) --no-print-directory --directory=$$i kernel-package ; \
		fi ; \
   done

sanity-check:
	for category in $(CATEGORIES) ; do \
		if [ ! -d ${CURDIR}/$$category ] ; then \
			echo "Warning : $$category folder is missing, recursive targets may fail or produce incomplete set of binaries." ; \
		fi ; \
		if [ ! -e "${CURDIR}/$$category/buildsystem" ] ; then \
			echo "buildsystem symlink in ${CURDIR}/$$category is missing or target does not exist. It should be a symlink to ../buildsystem" ; \
			echo "You can fix with the following shell commands :" ; \
			echo "ln -s ../buildsystem ${CURDIR}/$$category/buildsystem" ; \
			echo "git add ${CURDIR}/$$category/buildsystem" ; \
			$(call dft_error ,200103-01) ; \
		fi ; \
		if [ ! $(shell readlink ${CURDIR}/$$category/buildsystem) = "../$(DFT_BUILDSYSTEM)" ] ; then \
			echo "buildsystem symlink in ${CURDIR}/$$category must link to ../$(DFT_BUILDSYSTEM)" ; \
			echo "It targets to $(shell readlink ${CURDIR}/$$category/buildsystem)" ; \
			echo "You can fix with the following shell commands :" ; \
			echo "git rm -f ${CURDIR}/$$category/buildsystem" ; \
			echo "ln -s ../buildsystem ${CURDIR}/$$category/buildsystem" ; \
			echo "git add ${CURDIR}/$$category/buildsystem" ; \
			$(call dft_error ,200103-02) ; \
		fi ; \
		if [ ! -e "${CURDIR}/$$category/Makefile" ] ; then \
			echo "Makefile symlink in ${CURDIR}/$$category is missing or target does not exist. It should be a symlink to ../buildsystem/category.makefile" ; \
			echo "You can fix with the following shell commands :" ; \
			echo "ln -s ../$(buildsystem)/category.makefile $$category/Makefile" ; \
			echo "git add ${CURDIR}/$$category/Makefile" ; \
			$(call dft_error ,1091102-01) ; \
		fi ; \
		if [ ! $(shell readlink ${CURDIR}/$$category/Makefile) = "../$(buildsystem)/category.makefile" ] ; then \
			echo "Makefile symlink in ${CURDIR}/$$category must link to ../$(buildsystem)/category.makefile" ; \
			echo "It targets to $(shell readlink ${CURDIR}/$$category/Makefile)" ; \
			$(call dft_error ,191103-01) ; \
		fi ; \
		if [ -f ${CURDIR}/$$category/Makefile ] ; then \
			$(MAKE) --no-print-directory --directory=$$category sanity-check ; \
		else  \
			echo "DEBUG: Makefile is missing in ${CURDIR}/$$category" ; \
		fi ; \
		for board in `find $$category -mindepth 1 -maxdepth 1 -type d | tr / \  | cut --delimiter=\  --fields=2` ; do \
			if [ ! -f sbit/$$board.sbit.yml ] ; then \
				echo "Missing board support tests description file sbit/$$board.sbit.yml" ; \
				$(call dft_error ,200819-01) ; \
				fi ; \
	  done ; \
		if [ ! -d ${CURDIR}/$$category ] ; then \
			echo "Warning : $$category folder is missing, recursive targets may fail or produce incomplete set of binaries." ; \
		fi ; \
	done

# Forward target call to subfolders where are stored the board.mk files specifying board architecture
# $(MAKE) $@ --no-print-directory --directory=$(category) board-arch=$(arch) ;
list-boards:
	@MY_ARCH=$(board-arch) ; \
	if [ "$(board-arch)" = "armhf" ] ; then \
		MY_ARCH="armv7l"; \
	fi ; \
	if [ "$(board-arch)" = "arm64" ] ; then \
		MY_ARCH="aarch64"; \
	fi ; \
	if [ "$(board-arch)" = "amd64" ] ; then \
		MY_ARCH="x86_64"; \
	fi ; \
	if [ ! "$(category)" = "" ] ; then \
		if [ ! "$(board-arch)" = "" ] ; then \
			$(MAKE) $@ --no-print-directory --directory=$(category) board-arch=$$MY_ARCH verbosity=$(verbosity); \
		else \
			$(MAKE) $@ --no-print-directory --directory=$(category) verbosity=$(verbosity); \
		fi ; \
	else \
	for category in $(filter-out $(MAKE_FILTERS),$(shell find . -mindepth 1 -maxdepth 1 -type d -printf '%P\n')) ; do \
		if [ ! "$$MY_ARCH" = "" ] ; then \
			$(MAKE) $@ --no-print-directory --directory=$$category board-arch=$$MY_ARCH verbosity=$(verbosity); \
		else \
			$(MAKE) $@ --no-print-directory --directory=$$category verbosity=$(verbosity); \
		fi ; \
	done ; \
	fi | sort -u ;

list-architectures:
	if [ ! "$(category)" = "" ] ; then \
			$(MAKE) $@ --no-print-directory --directory=$(category) verbosity=$(verbosity); \
	fi | sort -u ;

show-u-boot-available-upgrade:
	@for category in $(CATEGORIES) ; do \
		if [ -f $$category/Makefile ] ; then \
			$(MAKE) --no-print-directory --directory=$$category $@ board-arch=$(board-arch) verbosity=$(verbosity); \
		fi ; \
	done

show-kernel-available-upgrade:
	@for category in $(CATEGORIES) ; do \
		if [ -f $$category/Makefile ] ; then \
			$(MAKE) --no-print-directory --directory=$$category $@ board-arch=$(board-arch) verbosity=$(verbosity); \
		fi ; \
	done
