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
# Copyright 2016 DFT project (http://www.debianfirmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#

# Defines board name
BOARD_NAME  = orangepi-zero-plus

# Defines boards architecture (armv7l, armv6l, aarch64, x86_64, i386, etc.)
BOARD_ARCH  = aarch64

# Defines the default dtb to use (symlink used by generic boot.scr)
DEFAULT_DTB = unknown

# Defines if all dtb should be included in the generated package (uncomment
# and set value to 1) or if only default dtb is included (keep commented or
# set the value to 0) 
# INCLUDE_ALL_DTB_IN_PACKAGE = 0
