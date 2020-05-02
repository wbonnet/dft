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

# ------------------------------------------------------------------------------
#
# Target that cal the dft command line tool to build the image
#
build-image:
	@echo "appel a dft en cli"

# ------------------------------------------------------------------------------
#
# Checks that all mandatory files are available
#
check-sanity:
l outil dft controle pas des trucs aussi?
firmware.yml
image-firmware.yml
image-rootfs.yml
project-firmware.yml
project-rootfs.yml
repositories.yml -> /usr/share/dft/library/repositories/repository-debian-fr-stretch.yml
rootfs.yml -> /usr/share/dft/library/rootfs/rootfs-netshell.yml
variables-orangepi-zero.yml
variables.yml -> /usr/share/dft/examples/rootfs-projects/netshell/variables.yml


# ------------------------------------------------------------------------------
#
# Target that prints the help
#
help:
	@echo "DEBUG help in board-image.makdefile"
	@echo "Available targets are :"
	@echo "   build-image             Build the $(BOARD_NAME) board image"
	@echo "   help                    Display this help"

