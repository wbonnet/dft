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

import logging, os, subprocess, shutil, tempfile, distutils
from distutils import dir_util, file_util
from cli_command import CliCommand

# TODO classe de base

#
#    Class GenerateContentInformation
#
class GenerateContentInformation(CliCommand): 
  """This class implements the methods needed to generate the output desribing
  rootfs content
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
  # generate_content_information
  #
  # -------------------------------------------------------------------------
  def generate_content_information(self):
    """This method implement the business logic of content generation.
    Information provided is the list of packages, TBD

    It calls dedicated method for each step. The main steps are :
    . Generate information about installed packages
    . Generate vulnerabilities information using debsecan
    . Generate security information using openscap
    . Generate file information (list, size, fingerprint, etc.)
    . Generate antivirus execution report
    """

    # Check if we are working with foreign arch, then ... 
    if self.use_qemu_static == True:
      # QEMU is used, and we have to install it into the target
      self.setup_qemu()

    #
    # Generate the packages information 
    #
    if "packages" in self.project.content_information_definition:
      logging.debug("Packages information generation is activated")
      self.generate_packages_information()
    else:
      logging.info("Packages information generation is deactivated")

    #
    # Generate the vulnerabilities information 
    #
    if "vulnerabilities" in self.project.content_information_definition:
      logging.debug("Vulnerabilities information generation is activated")
      self.generate_vulnerabilities_information()
    else:
      logging.info("Vulnerabilities information generation is deactivated")

    #
    # Generate the security information 
    #
    if "security" in self.project.content_information_definition:
      logging.debug("Security information generation is activated")
      self.generate_security_information()
    else:
      logging.info("Security information generation is deactivated")

    #
    # Generate the files information 
    #
    if "files" in self.project.content_information_definition:
      logging.debug("File information generation is activated")
      self.generate_files_information()
    else:
      logging.info("Files information generation is deactivated")

    #
    # Generate the anti-virus information 
    #
    if "anti-virus" in self.project.content_information_definition:
      logging.debug("Anti-virus information generation is activated")
      self.generate_antivirus_information()
    else:
      logging.info("Anti-virus information generation is deactivated")

    # Remove QEMU if it has been isntalled. It has to be done in the end
    # since some cleanup tasks could need QEMU
    if self.use_qemu_static == True:
      self.cleanup_qemu()

  # -------------------------------------------------------------------------
  #
  # generate_packages_information
  #
  # -------------------------------------------------------------------------
  def generate_packages_information(self):
    """This method implement the generation of information about packages.
    It relies on calls to dpkg and apt-cache in the chrooted environment.
    """

    # Generate the dpkg command to retrieve the list of installed packages
    sudo_command  = "LANG=C sudo chroot " + self.project.rootfs_mountpoint + " dpkg -l | tail -n +6"
    self.execute_command(sudo_command)

    # Test if we have to generate the package name in the output
    if "generate-package-name" in self.project.content_information_definition["packages"]:
      if self.project.content_information_definition["packages"]["generate-package-name"] == True:
        logging.warning("TODO : generate-package-name")

    # Test if we have to generate the package version in the output
    if "generate-package-version" in self.project.content_information_definition["packages"]:
      if self.project.content_information_definition["packages"]["generate-package-version"] == True:
        logging.warning("TODO : generate-package-version")

    # Test if we have to generate the package description in the output
    if "generate-package-description" in self.project.content_information_definition["packages"]:
      if self.project.content_information_definition["packages"]["generate-package-description"] == True:
        logging.warning("TODO : generate-package-description")

    # Test if we have to generate the package status in the output
    if "generate-package-status" in self.project.content_information_definition["packages"]:
      if self.project.content_information_definition["packages"]["generate-package-status"] == True:
        logging.warning("TODO : generate-package-status")

    # Test if we have to generate the package architecture in the output
    if "generate-package-architecture" in self.project.content_information_definition["packages"]:
      if self.project.content_information_definition["packages"]["generate-package-architecture"] == True:
        logging.warning("TODO : generate-package-architecture")

    # Test if we have to generate the package md5 in the output
    if "generate-package-md5" in self.project.content_information_definition["packages"]:
      if self.project.content_information_definition["packages"]["generate-package-md5"] == True:
        logging.warning("TODO : generate-package-md5")

    # Test if we have to generate the package sha256 in the output
    if "generate-package-sha256" in self.project.content_information_definition["packages"]:
      if self.project.content_information_definition["packages"]["generate-package-sha256"] == True:
        logging.warning("TODO : generate-package-sha256")

    # Test if we have to generate the package size in the output
    if "generate-package-size" in self.project.content_information_definition["packages"]:
      if self.project.content_information_definition["packages"]["generate-package-size"] == True:
        logging.warning("TODO : generate-package-size")

    # Test if we have to generate the package installed-size in the output
    if "generate-package-installed-size" in self.project.content_information_definition["packages"]:
      if self.project.content_information_definition["packages"]["generate-package-installed-size"] == True:
        logging.warning("TODO : generate-package-installed-size")



  # -------------------------------------------------------------------------
  #
  # generate_files_information
  #
  # -------------------------------------------------------------------------
  def generate_files_information(self):
    """This method implement the generation of information about files.
    Informationare extracted from the host information, not the chroot.
    """

    pass



  # -------------------------------------------------------------------------
  #
  # generate_antivirus_information
  #
  # -------------------------------------------------------------------------
  def generate_antivirus_information(self):
    """This method implement the generation of information aboutanti-virus
    analysis. It relies on call to an antivirus in the chrooted environment.
    """

    pass



  # -------------------------------------------------------------------------
  #
  # generate_security_information
  #
  # -------------------------------------------------------------------------
  def generate_security_information(self):
    """This method implement the generation of information about security.
    It relies on call to openscap in the chrooted environment.
    """

    # TODO need purge ?
    pass



  # -------------------------------------------------------------------------
  #
  # generate_vulnerabilities_information
  #
  # -------------------------------------------------------------------------
  def generate_vulnerabilities_information(self):
    """This method implement the generation of information about 
    vulnerabilities. It relies on call to debsecan and apt-cache in the 
    chrooted environment.
    """
 
    # Check if debsecan is installed in the chrooted environment
    if os.path.isfile( self.project.rootfs_mountpoint + "/usr/bin/debsecan") == False:
      # If not, test if it has to be installed, or should it fail ? 
      # Default behavior is to install debsecan if missing and to remove
      # it if it has been installed in thismethod context (and not in the
      # baseos)
      # If key is not defined, then set its default value      
      if self.project.content_information_definition["configuration"] != None:
        if "install-missing-software" not in self.project.content_information_definition["configuration"]:
          logging.debug("Setting default value of install-missing-software to False")
          self.project.content_information_definition["configuration"]["install-missing-software"] = False
      else:
        logging.debug("Setting default value of install-missing-software to False")
        self.project.content_information_definition["configuration"] = {'install-missing-software': False}

      if self.project.content_information_definition["configuration"]["install-missing-software"] == True:
        logging.info("Installing debsecan in rootfs")

        # Install missing packages into the chroot
        sudo_command  = "sudo chroot " + self.project.rootfs_mountpoint 
        sudo_command += " /usr/bin/apt-get install --no-install-recommends"
        sudo_command += " --yes --allow-unauthenticated debsecan"
        self.execute_command(sudo_command)

        # Set the flag used tomark that we install debsecan and we have to 
        # remove it before exiting the application
        need_to_remove_debsecan = True

      # The tool is missing and installation is not allowed,thus either we
      # allowed to skip this stage, or we fail and exit
      else:
        # If key is not defined, then set its default value
        if self.project.content_information_definition["configuration"] != None:
          if "skip-on-missing-software" not in self.project.content_information_definition["configuration"]:
            logging.debug("Setting default value of skip-on-missing-software to False")
            self.project.content_information_definition["configuration"]["skip-on-missing-software"] = True
        else:
          logging.debug("Setting default value of skip-on-missing-software to False")
          self.project.content_information_definition["configuration"] = {'skip-on-missing-software': True}

        # Check if skipping is allowed or not
        if self.project.content_information_definition["configuration"]["skip-on-missing-software"] == True:
          logging.warning("Skipping vulnerabilities content generation. Debsecan is missing and instalation not allowed by configuration file.")
          return
        else:
          # Skipping is deactivated, so is installation, thus it fails             
          logging.error("Debsecan is missing and instalation not allowed by configuration file.")
          logging.error("Please consider to add skip-on-on-missing-software or install-mising-software in configuration file")
          logging.critical("Generation canot continue, execution is aborted.")
          exit(1)

    # Generate the debsecan execution command
    sudo_command  = "sudo chroot " + self.project.rootfs_mountpoint 
    sudo_command += " /usr/bin/debsecan"
    self.execute_command(sudo_command)

    # Test if debsecan has to be removed
    if need_to_remove_debsecan == True:
      logging.info("Removing debsecan in rootfs")

      # Remove extra packages into the chroot
      sudo_command  = "sudo chroot " + self.project.rootfs_mountpoint 
      sudo_command += " /usr/bin/apt-get remove --yes debsecan"
      self.execute_command(sudo_command)
