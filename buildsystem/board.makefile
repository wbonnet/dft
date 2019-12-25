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
# Copyright 2016 DFT project (http://www.firmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#

# Defines variables specific to u-boot
SW_NAME     = u-boot

# Build system sould be available under board folder as a symlink. Keep it
# locally available under board folder computing a relative path is a nightmare
# and does not work in all cases. Environment variables are not git friendly
# since git add will loose variable name and generate an absolute path, which
# is not comptible with user need ans or workspace relocation nor packagng needs.
# better solutions wille be really welcomeds contributions.
buildsystem := buildsystem
include board.mk
include $(buildsystem)/dft.mk

# Do not recurse the following subdirs
MAKE_FILTERS = files Makefile README.md
SW_NAME      = SW_NAME_undefined_at_board_level

# ------------------------------------------------------------------------------
#
# Targets not associated with a file (aka PHONY)
#
.PHONY: help clean mrproper

sanity-check:
	@echo "Checking $(BOARD_NAME) board definition" ;
	@if [ ! -f "board.mk" ] ; then \
		pwd ; \
		echo "file board.mk is missing in directory ${CURDIR}" ; \
	        $(call dft_error ,191112-01) ; \
	fi ;
	@if [ ! -d "${CURDIR}/kernel" ] ; then \
		echo "kernel directory is missing in i${CURDIR}. It should contains a symlink to the generic makefile for Linux kernel" ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir -p ${CURDIR}/kernel" ; \
		echo "ln -s $(buildsystem)/linux-kernel.makefile ${CURDIR}/kernel/Makefile" ; \
		echo "git add ${CURDIR}/kernel" ; \
		echo "error 191114-01" ; \
		exit 1 ; \
	fi ;
	@if [ ! -d "${CURDIR}/kernel/defconfig" ] ; then \
		echo "defconfig directory is missing in ${CURDIR}/kernel. It is used to store kernel configuration files. It should at least contain a hidden empty file .gitkeep until first kernel version is added for $(BOARD_NAME)" ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir -p ${CURDIR}/kernel/defconfig" ; \
		echo "touch ${CURDIR}/kernel/defconfig/.gitkeep" ; \
		echo "git add ${CURDIR}/kernel/defconfig" ; \
		echo "error 191114-03" ; \
		exit 1 ; \
	fi ;
	@if [ ! -d "${CURDIR}/u-boot/files" ] ; then \
		echo "files directory is missing in ${CURDIR}/u-boot. It is used to store u-boot installation procedures. It should at least contain a hidden empty file .gitkeep until first uboot version is added for $(BOARD_NAME)" ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir -p ${CURDIR}/u-boot/files" ; \
		echo "touch ${CURDIR}/u-boot/files/.gitkeep" ; \
		echo "git add ${CURDIR}/u-boot/files" ; \
		echo "error 191117-01" ; \
		exit 1 ; \
	fi ;
	@if [ ! -d "${CURDIR}/u-boot" ] ; then \
		echo "u-boot directory is missing in ${CURDIR}. It should contains a symlink to the generic makefile for u-boot" ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir -p ${CURDIR}/u-boot" ; \
		echo "ln -s $(buildsystem)/u-boot.makefile ${CURDIR}/u-boot/Makefile" ; \
		echo "git add ${CURDIR}/u-boot" ; \
		echo "error 191114-02" ; \
		exit 1 ; \
	fi ;
	@if [ ! "$(shell readlink ${CURDIR}/u-boot/Makefile)" = "../$(buildsystem)/u-boot.makefile" ] ; then \
		echo "target of symlink Makefile should be ../$(buildsystem)/u-boot.makefile in directory ${CURDIR}/u-boot" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f ${CURDIR}/u-boot/Makefile" ; \
		echo "mkdir -p ${CURDIR}/u-boot" ; \
		echo "ln -s $(buildsystem)/u-boot.makefile ${CURDIR}/u-boot/Makefile" ; \
		echo "git add ${CURDIR}/u-boot/Makefile" ; \
		echo "error 191114-01" ; \
		exit 1 ; \
	fi ;
	@if [ ! "$(shell readlink ${CURDIR}/kernel/Makefile)" = "../$(buildsystem)/linux-kernel.makefile" ] ; then \
		echo "target of symlink Makefile should be ../$(buildsystem)/linux-kernel.makefile in directory ${CURDIR}/kernel" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f ${CURDIR}/kernel/Makefile" ; \
		echo "mkdir -p ${CURDIR}/kernel" ; \
		echo "ln -s ../$(buildsystem)/linux-kernel.makefile ${CURDIR}/kernel/Makefile" ; \
		echo "git add ${CURDIR}/kernel/Makefile" ; \
		echo "error 191114-02" ; \
		$(call dft_error "error 191114-02") \
		exit 1 ; \
	fi ;
	@if [ ! -L "kernel/board.mk" ] ; then \
		echo "board.mk symlink to ../board.mk is missing in directory ${CURDIR}/kernel" ; \
		echo "You can fix with the following commands : " ; \
		if [  -f "kernel/board.mk" ] ; then \
			echo "git rm ${CURDIR}/kernel/board.mk" ; \
		fi ; \
		echo "ln -s ../board.mk ${CURDIR}/kernel/board.mk" ; \
		echo "git add ${CURDIR}/kernel/board.mk" ; \
		echo "error 1911118-01" ; \
		exit 1 ; \
	fi ;
	@if [ ! "$(shell readlink ${CURDIR}/kernel/board.mk)" = "../board.mk" ] ; then \
		echo "target of symlink board.mk should be ../board.mk in directory ${CURDIR}/kernel" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f ${CURDIR}/kernel/board.mk" ; \
		echo "ln -s ../board.mk ${CURDIR}/kernel/board.mk" ; \
		echo "git add ${CURDIR}/kernel/board.mk" ; \
		echo "error 1911118-02" ; \
		exit 1 ; \
	fi ;
	@if [ ! -L "u-boot/board.mk" ] ; then \
		echo "board.mk symlink to ../board.mk is missing in directory ${CURDIR}/u-boot" ; \
		echo "You can fix with the following commands : " ; \
		if [  -f "u-boot/board.mk" ] ; then \
			echo "git rm ${CURDIR}/u-boot/board.mk" ; \
		fi ; \
		echo "ln -s ../board.mk ${CURDIR}/u-boot/board.mk" ; \
		echo "git add ${CURDIR}/u-boot/board.mk" ; \
		echo "error 1911118-03" ; \
		exit 1 ; \
	fi ;
	@if [ ! "$(shell readlink ${CURDIR}/u-boot/board.mk)" = "../board.mk" ] ; then \
		echo "target of symlink board.mk should be ../board.mk in directory ${CURDIR}/u-boot" ; \
		echo "You can fix with the following commands : " ; \
		echo "git rm -f ${CURDIR}/u-boot/board.mk" ; \
		echo "ln -s ../board.mk ${CURDIR}/u-boot/board.mk" ; \
		echo "git add ${CURDIR}/u-boot/board.mk" ; \
		echo "error 1911118-04" ; \
		exit 1 ; \
	fi ;
	@make -C u-boot sanity-check
	@make -C kernel sanity-check
	@for version in $(find . -mindepth 1 -maxdepth 1 -type d ) ; do \
		cd $$version && $(MAKE) $*  && cd .. ; \
        done

# Build only u-boot  package target
u-boot-package:
	@echo "u-boot-package from board.makefile" ;
	pwd ; \
	cd u-boot && $(MAKE) package && cd .. ;

# Build only linux kernel an package target
kernel-package:
	@echo "kernel-package from board.makefile" ;
	cd kernel && $(MAKE) package && cd .. ;

# Catch all target. Call the same targets in each subfolder
%:
	@echo "target $@ is called in board.makefile"
	@for i in $(filter-out $(MAKE_FILTERS),$(shell find . -mindepth 1 -maxdepth 1 -type d )) ; do \
		echo "examen de $$i" ; \
		if [ -f $$i/Makefile ] ; then \
			cd $$i && $(MAKE) $* && cd .. ; \
		fi ; \
        done
