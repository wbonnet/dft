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

""" This module is in charge of outputing information about the baseos (or rootfs)
content. Information ca be output to different format such as csv, yaml, xml, or json.
"""

import logging
import os
import tempfile
from cli_command import CliCommand

# TODO classe de base

#
#    Class ContentInformationOutputWriter
#
class ContentInformationOutputWriter(CliCommand):
  """This class implements the writer in charge of doing real output to the
  target defined in the configuration file. It can eithertarget a stream
  (stdout) or a file, using different format (csv yaml json xml).
  """

  # -------------------------------------------------------------------------
  #
  # __init__
  #
  # -------------------------------------------------------------------------
  def __init__(self, configuration):
    """Default constructor
    """

    # Initialize ancestor
#    CliCommand.__init__(self, dft, project)

    # Store the configuration dictionnary
    self.configuration = configuration
    self.output_file = None

  # -------------------------------------------------------------------------
  #
  # initialize
  #
  # -------------------------------------------------------------------------
  def Initialize(self, target):
    """This method initiliaze the output writer accorsing to the target
    argument. Target is one of the kind of output (packages, files, etc). The
    method does configuration checks, such as valid output format, target,
    etc. If configuration is valid, it opens the file or stream for output.
    """

    # Control output configuration parameters
    if self.configuration["configuration"]["output"]["format"] == "csv":
      logging.debug("Content information is output to CSV format")
    elif self.configuration["configuration"]["output"]["format"] == "yaml":
      logging.debug("Content information is output to YAML format")
    elif self.configuration["configuration"]["output"]["format"] == "json":
      logging.debug("Content information is output to JSON format")
      logging.error("Format is not yet available")
      exit(1)
    elif self.configuration["configuration"]["output"]["format"] == "xml":
      logging.debug("Content information is output to XML format")
      logging.error("Format is not yet available")
      exit(1)
    else:
      logging.error("Unknow output format " +
                    self.configuration["configuration"]["output"]["format"])
      exit(1)

    # Slect and create the output
    if self.configuration["configuration"]["output"]["target"] == "file":
      # Create a temporary file for output
      self.output_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
      logging.debug("Content information is output to a file")
    elif self.configuration["configuration"]["output"]["target"] == "stdout":
      logging.debug("Content information is output to stdout")
      logging.error("Output to stdout is not yet available")
      exit(1)
    else:
      logging.error("Unknow output TARGET " +
                    self.configuration["configuration"]["output"]["target"])
      exit(1)

  # -------------------------------------------------------------------------
  #
  # FlushAndClose
  #
  # -------------------------------------------------------------------------
  def FlushAndClose(self):
    """This method is in charg of flushing all the output and close opened
    files
    """

# TODO stream ?
# TODO flush ?

    # Test if the output file has been opened
    if self.output_file != None:
      # Yes then close it
      self.output_file.close()
      self.output_file = None

    # Move the target file to the right place ?
    # Depends on how we handle temp files
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
    CliCommand.__init__(self, dft, project)

    # Create the output writer object
    self.OutputWriter = ContentInformationOutputWriter(self.project.content_information_definition)



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

    # Check that there is a content definition file first
    print (self.project)
    if self.project.content_information_definition is not None:
      self.project.logging.critical("The content generation file is not defined in project file")
      exit(1)

    # Check if we are working with foreign arch, then ...
    if self.use_qemu_static:
      # QEMU is used, and we have to install it into the target
      self.setup_qemu()

    #
    # Generate the packages information
    #
    if self.project.dft.generate_all_information or self.project.dft.generate_packages_information:
      if "packages" in self.project.content_information_definition:
        logging.debug("Packages information generation is activated")
        self.generate_packages_information()
      else:
        logging.info("Packages information generation is deactivated")

    #
    # Generate the vulnerabilities information
    #
    if self.project.dft.generate_all_information or self.project.dft.generate_vulnerabilities_information:
      if "vulnerabilities" in self.project.content_information_definition:
        logging.debug("Vulnerabilities information generation is activated")
        self.generate_vulnerabilities_information()
      else:
        logging.info("Vulnerabilities information generation is deactivated")

    #
    # Generate the security information
    #
    if self.project.dft.generate_all_information or self.project.dft.generate_security_information:
      if "security" in self.project.content_information_definition:
        logging.debug("Security information generation is activated")
        self.generate_security_information()
      else:
        logging.info("Security information generation is deactivated")

    #
    # Generate the files information
    #
    if self.project.dft.generate_all_information or self.project.dft.generate_files_information:
      if "files" in self.project.content_information_definition:
        logging.debug("File information generation is activated")
        self.generate_files_information()
      else:
        logging.info("Files information generation is deactivated")

    #
    # Generate the anti-virus information
    #
    if self.project.dft.generate_all_information or self.project.dft.generate_antivirus_information:
      if "anti_virus" in self.project.content_information_definition:
        logging.debug("Anti-virus information generation is activated")
        self.generate_antivirus_information()
      else:
        logging.info("Anti-virus information generation is deactivated")

    # Remove QEMU if it has been isntalled. It has to be done in the end
    # since some cleanup tasks could need QEMU
    if self.use_qemu_static:
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

    # Initialize the output writer for packages content generation
    self.OutputWriter.Initialize("packages")

    # Generate the dpkg command to retrieve the list of installed packages
    sudo_command = "LANG=C sudo chroot " + self.project.rootfs_mountpoint + " dpkg -l | tail -n +6"
    sudo_command_output = self.execute_command(sudo_command)

    # Iterate the output of the dpkg process:
    for binaryline in sudo_command_output.splitlines():
      # Each fields is stored into a variable to easy manipulation and
      # simplify code. First get the array of words converted to UTF-8
      line = binaryline.decode('utf-8').split()

      # Extract each fields
      pkg_status = line[0]
      pkg_name = line[1]
      pkg_version = line[2]
      pkg_arch = line[3]
      # space is used as a separator to rebuild the description
      pkg_description = " ".join(line[4:])

      # Flag used to know if we need a space separator between fields
      add_spacer = False

      # Starts with empty output
      output = ""

      # Test if we have to generate the package status in the output
      if "generate_package_status" in self.project.content_information_definition["packages"]:
        if self.project.content_information_definition["packages"]["generate_package_status"]:
      # Test if we have to generate the package description in the output
          output += pkg_status
          add_spacer = True

      # Test if we have to generate the package name in the output
      if "generate_package_name" in self.project.content_information_definition["packages"]:
        if self.project.content_information_definition["packages"]["generate_package_name"]:
          if add_spacer:
            output += " "
          output += pkg_name
          add_spacer = True

      # Test if we have to generate the package version in the output
      if "generate_package_version" in self.project.content_information_definition["packages"]:
        if self.project.content_information_definition["packages"]["generate_package_version"]:
          if add_spacer:
            output += " "
          output += pkg_version
          add_spacer = True

      # Test if we have to generate the package architecture in the output
      if "generate_package_architecture" in self.project.content_information_definition["packages"]:
        if self.project.content_information_definition["packages"]["generate_package_architecture"]:
          if add_spacer:
            output += " "
          output += pkg_arch
          add_spacer = True

      # Test if we have to generate the package md5 in the output
      if "generate_package_md5" in self.project.content_information_definition["packages"]:
        if self.project.content_information_definition["packages"]["generate_package_md5"]:
          # Generate the apt-cache show command to retrieve the MD5sum
          # Grp the keyword and print second word
          sudo_command = "LANG=C sudo chroot " + self.project.rootfs_mountpoint
          sudo_command += " apt-cache show " + pkg_name + " | grep ^MD5sum | awk '{ print $2 }'"
          sudo_command_output = self.execute_command(sudo_command)
          if add_spacer:
            output += " "
          output += sudo_command_output.decode('utf-8')
          add_spacer = True

      # Test if we have to generate the package sha256 in the output
      if "generate_package_sha256" in self.project.content_information_definition["packages"]:
        if self.project.content_information_definition["packages"]["generate_package_sha256"]:
          # Generate the apt-cache show command to retrieve the SHA256
          # Grp the keyword and print second word
          sudo_command = "LANG=C sudo chroot " + self.project.rootfs_mountpoint
          sudo_command += " apt-cache show " + pkg_name + " | grep ^SHA256 | awk '{ print $2 }'"
          sudo_command_output = self.execute_command(sudo_command)
          if add_spacer:
            output += " "
          output += sudo_command_output.decode('utf-8')
          add_spacer = True

      # Test if we have to generate the package size in the output
      if "generate_package_size" in self.project.content_information_definition["packages"]:
        if self.project.content_information_definition["packages"]["generate_package_size"]:
          # Generate the apt-cache show command to retrieve the Size
          # Grp the keyword and print second word
          sudo_command = "LANG=C sudo chroot " + self.project.rootfs_mountpoint
          sudo_command += " apt-cache show " + pkg_name + " | grep ^Size | awk '{ print $2 }'"
          sudo_command_output = self.execute_command(sudo_command)
          if add_spacer:
            output += " "
          output += sudo_command_output.decode('utf-8')
          add_spacer = True

      # Test if we have to generate the package installed-size in the output
      if "generate_package_installed_size" in self.project.content_information_definition["packages"]:
        if self.project.content_information_definition["packages"]["generate_package_installed_size"]:
          # Generate the apt-cache show command to retrieve the Installed-SizeMD5sum
          # Grp the keyword and print second word
          sudo_command = "LANG=C sudo chroot " + self.project.rootfs_mountpoint
          sudo_command += " apt-cache show " + pkg_name + " | grep ^Installed-Size | awk '{ print $2 }'"
          sudo_command_output = self.execute_command(sudo_command)
          if add_spacer:
            output += " "
          output += sudo_command_output.decode('utf-8')
          add_spacer = True

      # Test if we have to generate the package description in the output
      if "generate_package_description" in self.project.content_information_definition["packages"]:
        if self.project.content_information_definition["packages"]["generate_package_description"]:
          if add_spacer:
            output += " "
          output += pkg_description
          add_spacer = True

      print(output)

    # Flush all pending output and close stream or file
    self.OutputWriter.FlushAndClose()

  # -------------------------------------------------------------------------
  #
  # generate_files_information
  #
  # -------------------------------------------------------------------------
  def generate_files_information(self):
    """This method implement the generation of information about files.
    Informationare extracted from the host information, not the chroot.
    """

    # Initialize the output writer for packages content generation
    self.OutputWriter.Initialize("files")

    # Flush all pending output and close stream or file
    self.OutputWriter.FlushAndClose()



  # -------------------------------------------------------------------------
  #
  # generate_antivirus_information
  #
  # -------------------------------------------------------------------------
  def generate_antivirus_information(self):
    """This method implement the generation of information aboutanti-virus
    analysis. It relies on call to an antivirus in the chrooted environment.
    """

    # Initialize the output writer for packages content generation
    self.OutputWriter.Initialize("antivirus")

# Todo install clamav

    # Generate the dpkg command to retrieve the list of installed packages
    sudo_command = "LANG=C sudo chroot " + self.project.rootfs_mountpoint
    sudo_command += " clamscan --infected --recursive"
    sudo_command_output = self.execute_command(sudo_command)

    # Flush all pending output and close stream or file
    self.OutputWriter.FlushAndClose()



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

    # Initialize the output writer for packages content generation
    self.OutputWriter.Initialize("security")

    # Flush all pending output and close stream or file
    self.OutputWriter.FlushAndClose()



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

     # Initialize the output writer for packages content generation
    self.OutputWriter.Initialize("vulnerabilities")

    # Check if debsecan is installed in the chrooted environment
    if not os.path.isfile(self.project.rootfs_mountpoint + "/usr/bin/debsecan"):
      # If not, test if it has to be installed, or should it fail ?
      # Default behavior is to install debsecan if missing and to remove
      # it if it has been installed in thismethod context (and not in the
      # baseos)
      # If key is not defined, then set its default value
      if self.project.content_information_definition["configuration"] != None:
        if "install_missing_software" not in self.project.content_information_definition["configuration"]:
          logging.debug("Setting default value of install_missing_software to False")
          self.project.content_information_definition["configuration"]["install_missing_software"] = False
      else:
        logging.debug("Setting default value of install-missing-software to False")
        self.project.content_information_definition["configuration"] = {'install_missing_software': False}

      if self.project.content_information_definition["configuration"]["install_missing_software"]:
        logging.info("Installing debsecan in rootfs")

        # Install missing packages into the chroot
        sudo_command = "sudo chroot " + self.project.rootfs_mountpoint
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
          if "skip_on_missing_software" not in self.project.content_information_definition["configuration"]:
            logging.debug("Setting default value of skip_on_missing_software to False")
            self.project.content_information_definition["configuration"]["skip_on_missing_software"] = True
        else:
          logging.debug("Setting default value of skip_on_missing_software to False")
          self.project.content_information_definition["configuration"] = {'skip_on_missing_software': True}

        # Check if skipping is allowed or not
        if self.project.content_information_definition["configuration"]["skip_on_missing_software"]:
          logging.warning("Skipping vulnerabilities content generation. Debsecan is missing and instalation not allowed by configuration file.")
          return
        else:
          # Skipping is deactivated, so is installation, thus it fails
          logging.error("Debsecan is missing and instalation not allowed by configuration file.")
          logging.error("Please consider to add skip_on_missing_software or install_mising_software in configuration file")
          logging.critical("Generation canot continue, execution is aborted.")
          exit(1)

    # Generate the debsecan execution command
    sudo_command = "sudo chroot " + self.project.rootfs_mountpoint
    sudo_command += " /usr/bin/debsecan"
    self.execute_command(sudo_command)

    # Test if debsecan has to be removed
    if need_to_remove_debsecan:
      logging.info("Removing debsecan in rootfs")

      # Remove extra packages into the chroot
      sudo_command = "sudo chroot " + self.project.rootfs_mountpoint
      sudo_command += " /usr/bin/apt-get remove --yes debsecan"
      self.execute_command(sudo_command)

    # Flush all pending output and close stream or file
    self.OutputWriter.FlushAndClose()
  