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

# 
# Board level birectory generic Linux kernel makefile
#

# No need to recurse check target at version level
check :
	# Board level directory must contain defconfig folder storing config files for the different kernel versions
	@echo "Checking Linux kernel folder for board $(BOARD_NAME)" 
	@if [ ! -d "$(shell pwd)/defconfig" ] ; then \
		echo "defconfig directory is missing in $(shell pwd). It contains the configuration files of the different Linux kernel versions." ; \
		echo "You can fix with the following commands : " ; \
		echo "mkdir $(shell pwd)/defconfig" ; \
		echo "touch $(shell pwd)/defconfig.gitkeep" ; \
		echo "git add $(shell pwd)/defconfig.gitkeep" ; \
		false ; \
	fi ;
	@if [ ! -L "./Makefile" ] ; then \
		echo "Makefile symlink to ../../../../../buildsystem/shared/kernel.makefile is missing in $(shell pwd)" ; \
		false ; \
	fi ; 

help :
	@echo "Supported targets are"
	@echo 'check : Verify the availability of required items (files, symlinks, directories) and report missing.'
