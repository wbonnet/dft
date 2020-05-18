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

# Force bash use instead of sh which is a symlink to dash on Debian. Dash use
# a slightly different syntax for some operators. This way it a known shell.
SHELL := bash

# Include image variables definition
include ../board.mk
include image.mk

# ------------------------------------------------------------------------------
#
# Target that call the dft command line tool to build the image
#
build-image:
	echo "time command is only for cache profiling purpose and will be removed soon" ; \
	time sudo dft run_sequence --project project.yml --sequence produce-image  --log-level debug --config-file /home/william/.dftrc 

list-images:
	@echo $(IMAGE_NAME)

# ------------------------------------------------------------------------------
#
# Checks that all mandatory files are available
#
check-sanity:
	@echo "l outil dft controle pas des trucs aussi?"
	@echo "firmware.yml"
	@echo "image-firmware.yml"
	@echo "image-rootfs.yml"
	@echo "project-firmware.yml"
	@echo "project-rootfs.yml"
	@echo "repositories.yml -> /usr/share/dft/library/repositories/repository-debian-fr-stretch.yml"
	@echo "rootfs.yml -> /usr/share/dft/library/rootfs/rootfs-netshell.yml"
	@echo "variables-orangepi-zero.yml"
	@echo "variables.yml -> /usr/share/dft/examples/rootfs-projects/netshell/variables.yml"

# ------------------------------------------------------------------------------
#
# Target that prints the help
#
help:
	@echo "Available targets are :"
	@echo "   build-image             Build the $(BOARD_NAME) board image"
	@echo "   help                    Display this help"

