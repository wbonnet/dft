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

import logging, os, subprocess, shutil, distutils
from distutils import dir_util, file_util
from cli_command import CliCommand

# TODO heriter classe de base

#
#    Class StripRootFS
#
class StripRootFS(CliCommand): 
    """This class implements the methods needed to strip the base OS

    Stripping the base OS is the task to remove extra packages and files
    that should not be included inthe firmware. These files may come from
    different sources (istalled packages, manual creation, etc.)
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

        # Set the log level from the configuration
        logging.basicConfig(level=project.dft.log_level)


    # -------------------------------------------------------------------------
    #
    # strip_rootfs
    #
    # -------------------------------------------------------------------------
    def strip_rootfs(self):
        """This method implement the business logic of rootfs stripping.
        
TODO
        It calls dedicated method for each step. The main steps are :
        . 
        """

        logging.critical("Not yet available")
        exit(1)
