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
# Copyright 2018 DFT project (http://www.firmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#

# ------------------------------------------------------------------------------
#
# Used for output...
#
DISPLAY_TARGET_NOT_IMPLEMENTED = @echo "Target [$@] is not implemented !"
DISPLAY_COMPLETED_TARGET_NAME  = @echo "    completed [$@] "


# ------------------------------------------------------------------------------
#
# Cookie maker
#
COOKIE_DIR  ?= $(CURDIR)/.cookies
TARGET_DONE = @mkdir -p $(dir $(COOKIE_DIR)/$@) && touch $(COOKIE_DIR)/$@
