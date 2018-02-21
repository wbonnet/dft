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
# Copyright 2018 DFT project (http://www.debianfirmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#

# Includes common definition for all examples Makefiles
include ../../examples-common.mk

# ------------------------------------------------------------------------------
#
# Targets not associated with a file (aka PHONY)
#
.PHONY: create-rootfs upload-rootfs create-firmware upload-firmware create-firmware-update upload-firmware-update distclean clean

# ------------------------------------------------------------------------------
#
# Target that prints the help
#
help :
	@echo "Available targets are :"
	@echo '   create-firmware         Run the DFT sequence used to build the firmware image'
	@echo '   upload-firmware         Upload the firmware image to a remote server'
	@echo '                           (this target use the DFT_FIRMWARE_UPLOAD_SERVER and'
	@echo '                           DFT_FIRMWARE_UPLOAD_PATH variables from your shell env)'
	@echo '   create-firmware-update  Run the DFT sequence used to build a firmwareupdate image'
	@echo '   upload-firmware-update  Upload the firmware update image to a remote server'
	@echo '                           (this target also use the DFT_FIRMWARE_UPLOAD_SERVER and'
	@echo '                           DFT_FIRMWARE_UPLOAD_PATH variables from your shell env)'
	@echo '   create-rootfs           Runs the DFT sequence used to build the firmware image'
	@echo '   upload-rootfs           Runs the DFT sequence used to build the rootfs image'
	@echo '                           (this target use the DFT_ROOTFS_UPLOAD_SERVER and'
	@echo '                           DFT_ROOTFS_UPLOAD_PATH variables from your shell env)'
	@echo


# Run a full dft sequence to produce the firmware image
firmware:
	@if test -f $(COOKIE_DIR)/firmware ; then \
		true ; \
	else \
		sudo -E dft run_sequence --sequence produce-image --project project-firmware.yml ; \
	fi ;
	$(TARGET_DONE)

# Run a full dft sequence to produce the rootfs image
rootfs:
	@if test -f $(COOKIE_DIR)/rootfs ; then \
		true ; \
	else \
		sudo -E dft run_sequence --sequence produce-image --project project-rootfs.yml ; \
	fi ;
	$(TARGET_DONE)

# Upload the firmware to a remote server
upload-firmware: firmware
	@if test -f $(COOKIE_DIR)/upload-firmware ; then \
		true ; \
	else \
		echo "        running upload"  ; \
	 	if [ ! "" = "$(DFT_FIRMWARE_UPLOAD_SERVER)" ] && [ ! "" = "$(DFT_FIRMWARE_UPLOAD_PATH)" ] ; then \
			scp $(abspath $(PACKAGE_DIR))/*.deb $(DFT_FIRMWARE_UPLOAD_SERVER):$(DFT_FIRMWARE_UPLOAD_PATH) ; \
	 	else \
	 	    if [ "" = "$(DFT_FIRMWARE_UPLOAD_SERVER)" ] ; then \
			    echo "        Variable DFT_FIRMWARE_UPLOAD_SERVER is not set, please define it your shell environment."  ; \
			else \
			    echo "        DFT_FIRMWARE_UPLOAD_SERVER = $(DFT_FIRMWARE_UPLOAD_SERVER)."  ; \
			fi ; \
	 	    if [ "" = "$(DFT_FIRMWARE_UPLOAD_PATH)" ] ; then \
			    echo "        Variable DFT_FIRMWARE_UPLOAD_PATH is not set, please define it your shell environment."  ; \
			else \
			    echo "        DFT_FIRMWARE_UPLOAD_PATH = $(DFT_FIRMWARE_UPLOAD_PATH)."  ; \
			fi ; \
			false ; \
		fi ; \
	fi ;
	$(TARGET_DONE)

distclean: clean
clean:
	@rm -fr $(COOKIE_DIR)
