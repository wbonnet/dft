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

#
#    Class CliCommand
#
class CliCommand: 
    """This class implements the base class used for all command fro cli

       It provides method used in all the derivated command, such has
       sudo execution and error handling, qemu setup and tear down, etc
    """

    # -------------------------------------------------------------------------
    #
    # __init__
    #
    # -------------------------------------------------------------------------
    def __init__(self, dft, project):
        """Default constructor
        """

        # Object storing the tool configuration. This object holds all the 
        # definition of global configuration variales, such as tool installation
        # path, archive use, log level, etc
        self.dft = dft

        # Object storing the project definition. Project holds all the 
        # configuration and definition used by the different stage of 
        # the toolchain, including baseos definition
        self.project = project

        # Retrieve the architecture of the host
        self.host_arch = subprocess.check_output("dpkg --print-architecture", shell=True).decode('UTF-8').rstrip()

        # Boolean used to flag the use of QEMU static
        self.use_qemu_static =  (self.host_arch != project.target_arch)

        # Boolean used to flag if the cache archive is available. This value 
        # is set by the setup_configuration method. Default is False, to 
        # ensure it will be rebuild
        self.cache_archive_is_available = False
 
        # Flags used to remove 'mount bind' states
        self.proc_is_mounted   = False
        self.devpts_is_mounted = False
        self.devshm_is_mounted = False

        # Flag used to prevent multiple call to cleanup since cleanup is used
        # in exception processing
        self.doing_cleanup_installation_files = False

        # Set the log level from the configuration
        logging.basicConfig(level=project.dft.log_level)


#TODO faire remonter dans clase de base

    # -------------------------------------------------------------------------
    #
    # exec_sudo
    #
    # -------------------------------------------------------------------------
    def execute_command(self, command):
        """ This method run a command as a subprocess. Typical use case is 
        running sudo commands.

        This method is a wrapper to subprocess.run , and will be moved soon
        in a helper object. It provides mutalisation of error handling
        """

        try:
            logging.debug("running : " + command)
            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True)

        except subprocess.CalledProcessError as e:
            self.cleanup_installation_files()
            logging.critical("Error %d occured when executing %s" % (e.returncode, e.cmd))
            logging.debug("stdout")
            logging.debug("%s" % (e.stdout.decode('UTF-8')))
            logging.debug("stderr")
            logging.debug("%s" % (e.stderr.decode('UTF-8')))
            exit(1)


#TODO remonter ici le setup et le cleanup de qemu