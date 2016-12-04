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
# Debian Firmware Toolkit is the new name of Linux Firmware From Scratch
# Copyright 2014 LFFS project (http://www.linuxfirmwarefromscratch.org).  
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#

import logging, os, subprocess, tarfile, shutil, tempfile, distutils
from distutils import dir_util, file_util
from cli_command import CliCommand

#
#    Class AssembleFirmware
#
class AssembleFirmware(CliCommand): 
    """This class implements method needed to assemble the toolchain used to 
    assemble firmware inmemory when system is booting.

    Firmware assembling incudes the tasks of generating configuration files 
    for sqashfs stacking and initramfs generation. It also includes the 
    creation of the script used to handles reboot to preious version, and
    integrity check at start.
    """

    # -------------------------------------------------------------------------
    #
    # __init__
    #
    # -------------------------------------------------------------------------
    def __init__(self, dft, project):
        """Default constructor
        """

        # Initialize ancestor
        super().__init__(dft, project)

    # -------------------------------------------------------------------------
    #
    # assemble_firmware
    #
    # -------------------------------------------------------------------------
    def assemble_firmware(self):
        """This method implement the business logic of firmware assembling.
        
        Assembling a firmware, use as input the firmware file created from a 
        baseos and then generate the configuration files used to loading after 
        booting. The configuration is used to define how the filesystems are
        stacked, what should be the physical partitionning, ciphering, etc.

        It calls dedicated method for each step. The main steps are :
        . 
        """


# What is needed in the configuration file
# layout:
#   use unionfs or overlayfs 
#   defines mapping over squashfs
#   => direct write ?
#   - mountpoint:
#     type: sqasuhfs , partition, tmpfs
#     path:
#     mount_option:
#     auto_commit: False
# stacking ? 
# how to define cow ?

# security:
#   not at start, but need to check for hashes or signatures
#   how to handle ciphering, keygen, secure storage

# safety:
#   at start single bank
#   bank: 2

        logging.critical("Not yet available")
        exit(1)


