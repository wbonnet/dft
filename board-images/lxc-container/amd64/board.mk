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
# Copyright 2020 DFT project (http://www.firmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#

#
# Board global parameters
#

# The board name fragment will be used in package naming, path and files content generation
BOARD_NAME = lxc-container

# Board architecture as defined by uname -m (armv7l, mips, aarch64, x86_64, etc.)
BOARD_ARCH = x86_64


#
# No u-boot nor grub support for LXC containers
#
UBOOT_SUPPORT = 0
GRUB_SUPPORT = 0

#
# Linux Kernel is provided by host, thus no kernel definition nor generation or installation inside host
#
LINUX_KERNEL_SUPPORT = 0
