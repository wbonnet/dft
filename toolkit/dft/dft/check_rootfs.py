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


# TODO classe de base

#
#    Class CheckRootFS
#
class CheckRootFS(CliCommand): 
    """This class implements method needed to check the base OS content.

    The content of the rootfs can be checked for mising or forbidden 
    packages, files, directories and symlink. Attributes, versions and 
    content can also be checked
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

    # -------------------------------------------------------------------------
    #
    # check_rootfs
    #
    # -------------------------------------------------------------------------
    def check_rootfs(self):
        """This method implement the business logic of generating the rootfs. It calls
        dedicated method for each step. The main steps are :

        . setting up configuration (mostly rules and path to the rootfs to check)
        . setup QEMU if needed
        . check for packages
        . check for files, dirctories and symlink
        . cleanup QEMU if needed
        """

        logging.critical("Not yet available")
        exit(1)


        
    # -------------------------------------------------------------------------
    #
    # check_packages
    #
    # -------------------------------------------------------------------------
    def check_packages(self):
        """This method is in charge of contolling the pacages installed in the 
        rootfs according to the rules loaded from the configurtion file.

        Packages can have several status :
        . mandatory  =>  it MUST  be installed
        . allowed    =>  it CAN   be installed
        . forbidden  =>  it CAN'T be installed

        Version of packages can also be controlled. Available checks are :
        . min-version          => LOWER versions CAN'T be installed
        . max-version          => MORE RECENT versions CAN'T be installed
        . fixed-version        => ONE of the given version MUST be installed
                                  it is a list
        . blacklisted-version  => NONE of the given version CAN be installed
                                  it is a list
        """
        logging.info("starting to check installed packages")

# TODO traiter les paquet en rc ?
# TODO traiter les architectures ?

    # -------------------------------------------------------------------------
    #
    # check_files
    #
    # -------------------------------------------------------------------------
    def check_files(self):
        """This method is in charge of contolling the files (and also 
        directories and symlinks) installed in the rootfs according to the 
        rules loaded from the configurtion file.

        Files ia a term that identify any object in the file system. A 'file'
        can be a standard file, but also a directory or a symlink (special 
        devices are not handled, yet...). As a standard file, a package is a 
        file. 

        Checks on packages from what the check_packages method does. This 
        method wil lookfor the foo.deb file in itself, not if it is installed
        what is its versions etc. 

        Files can have several status :
        . mandatory  =>  it MUST  be installed
        . allowed    =>  it CAN   be installed
        . forbidden  =>  it CAN'T be installed

        A file is defined by it path. The following attributes can be checked :
        . type           file, directory or symlink. Default is file
        . owner          since owner and group can be either numric or text,   
        . group          it has to be checked inside the chrooted environment
        . mask
        . target         only if type is symlink
        . empty          only for files and directories (zero sized for file, 
                         and no centent at all for directories)
        . md5            file (or symlink target) checksum computed with MD5
        . sha1           file (or symlink target) checksum computed with SHA1
        . sha256         file (or symlink target) checksum computed with SHA256

        """
# TODO controler le sha dans les tests unitaires

        logging.info("starting to check installed packages")
