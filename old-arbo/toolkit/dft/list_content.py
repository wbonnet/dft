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

""" This module is in charge of outputing information about the rootfs (or rootfs)
content. Information ca be output to different format such as csv, yaml, xml, or json.
"""

import logging
import os
import tempfile
from dft.cli_command import CliCommand
from dft.enumkey import Key

#
#    Class ContentOutputWriter
#
class ContentOutputWriter(object):
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

    # Store the configuration dictionnary
    self.configuration = configuration
    self.output_file = None

    # Defines the object storing the items used for output. This variable is
    # a list of dictionnaries. Each item in the list is a line to output. The
    # item content is a dictionnaries. The keys are used when producing output
    # to format such as XML, JSON or YAML
    self.__output_buffer = list()

  # -------------------------------------------------------------------------
  #
  # initialize
  #
  # -------------------------------------------------------------------------
  def initialize(self, target):
    """This method initiliaze the output writer accorsing to the target
    argument. Target is one of the kind of output (packages, files, etc). The
    method does configuration checks, such as valid output format, target,
    etc. If configuration is valid, it opens the file or stream for output.
    """

    # Control output configuration parameters
    if self.configuration[Key.CONFIGURATION.value][Key.OUTPUT.value][Key.FORMAT.value] \
                                                                           == Key.CSV.value:
      logging.debug("Content information is output to CSV format")
    elif self.configuration[Key.CONFIGURATION.value][Key.OUTPUT.value][Key.FORMAT.value] \
                                                                           == Key.YAML.value:
      logging.debug("Content information is output to YAML format")
    elif self.configuration[Key.CONFIGURATION.value][Key.OUTPUT.value][Key.FORMAT.value] \
                                                                           == Key.JSON.value:
      logging.debug("Content information is output to JSON format")
      logging.error("Format is not yet available")
      exit(1)
    elif self.configuration[Key.CONFIGURATION.value][Key.OUTPUT.value][Key.FORMAT.value] \
                                                                           == Key.XML.value:
      logging.debug("Content information is output to XML format")
      logging.error("Format is not yet available")
      exit(1)
    else:
      logging.error("Unknow output format " +
                    self.configuration[Key.CONFIGURATION.value][Key.OUTPUT.value][Key.FORMAT.value])
      exit(1)

    # Select and create the output
    if self.configuration[Key.CONFIGURATION.value][Key.OUTPUT.value][Key.TARGET.value] \
                                                                           == Key.FILE.value:
      # Create a temporary file for output
      self.output_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
      logging.debug("Content information is output to a file")
    elif self.configuration[Key.CONFIGURATION.value][Key.OUTPUT.value][Key.TARGET.value] \
                                                                           == Key.STDOUT.value:
      logging.debug("Content information is output to stdout")
      logging.error("Output to stdout is not yet available")
      exit(1)
    else:
      logging.error("Unknow output TARGET " + self.configuration[Key.CONFIGURATION.value]\
                                                       [Key.OUTPUT.value][Key.TARGET.value])
      exit(1)



  # -------------------------------------------------------------------------
  #
  # append_item
  #
  # -------------------------------------------------------------------------
  def append_item(self, item):
    """Append an item to the output buffer. This method is provided to hide internals
    """

    # print(output)
    self.__output_buffer.append(item)



  # -------------------------------------------------------------------------
  #
  # flush_and_close
  #
  # -------------------------------------------------------------------------
  def flush_and_close(self):
    """This method is in charg of flushing all the output and close opened
    files
    """

    print(self.__output_buffer)

    # Test if the output file has been opened
    if self.output_file != None:
      # Yes then close it
      self.output_file.close()
      self.output_file = None

    # Move the target file to the right place ?
    # Depends on how we handle temp files



#
#    Class ListContent
#
class ListContent(CliCommand):
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
    self.output_writer = ContentOutputWriter(self.project.list_content)



  # -------------------------------------------------------------------------
  #
  # list_content
  #
  # -------------------------------------------------------------------------
  def list_content(self):
    """This method implement the business logic of content generation.
    Information provided is the list of packages, TBD

    It calls dedicated method for each step. The main steps are :
    . Generate information about installed packages
    . Generate vulnerabilities information using debsecan
    . Generate security information using openscap and lynis
    . Generate rootkit information using rkhunter
    . Generate file information (list, size, fingerprint, etc.)
    . Generate antivirus execution report
    """

    # output some activity log. Some operation may be quite long...
    logging.info("Starting to generate content information")

    # Check that there is a content definition file first
    if self.project.list_content is None:
      self.project.logging.critical("The content generation file is not defined in project file")
      exit(1)

    # Check if we are working with foreign arch, then ...
    if self.use_qemu_static:
      # QEMU is used, and we have to install it into the target
      self.setup_qemu()

    #
    # Generate the packages information
    #
    if self.project.dft.generate_all_information or self.project.dft.gen_packages_info:
      if Key.PACKAGES.value in self.project.list_content:
        logging.info("Starting to generate packages information")
        self.gen_packages_info()
      else:
        logging.info("Packages information generation is deactivated")

    #
    # Generate the vulnerabilities information
    #
    if self.project.dft.generate_all_information or self.project.dft.gen_vulnerabilities_info:
      if Key.VULNERABILITIES.value in self.project.list_content:
        logging.info("Starting to generate vulnerabilities information")
        self.gen_vulnerabilities_info()
      else:
        logging.info("Vulnerabilities information generation is deactivated")

    #
    # Generate the security information
    #
    if self.project.dft.generate_all_information or self.project.dft.gen_security_info:
      if Key.SECURITY.value in self.project.list_content:
        logging.info("Starting to generate security information")
        self.gen_security_info()
      else:
        logging.info("Security information generation is deactivated")

    #
    # Generate the rootkit information
    #
    if self.project.dft.generate_all_information or self.project.dft.gen_rootkit_info:
      if Key.ROOTKIT.value in self.project.list_content:
        logging.info("Starting to generate rootkit information")
        self.gen_rootkit_info()
      else:
        logging.info("Rootkit information generation is deactivated")

    #
    # Generate the files information
    #
    if self.project.dft.generate_all_information or self.project.dft.gen_files_info:
      if Key.FILES.value in self.project.list_content:
        logging.info("Starting to generate files information")
        self.gen_files_info()
      else:
        logging.info("Files information generation is deactivated")

    #
    # Generate the anti-virus information
    #
    if self.project.dft.generate_all_information or self.project.dft.gen_antivirus_info:
      if Key.ANTIVIRUS.value in self.project.list_content:
        logging.info("Starting to generate antivirus information")
        self.gen_antivirus_info()
      else:
        logging.info("Anti-virus information generation is deactivated")

    # Remove QEMU if it has been isntalled. It has to be done in the end
    # since some cleanup tasks could need QEMU
    if self.use_qemu_static:
      self.cleanup_qemu()



  # -------------------------------------------------------------------------
  #
  # gen_packages_info
  #
  # -------------------------------------------------------------------------
  def gen_packages_info(self):
    """This method implement the generation of information about packages.
    It relies on calls to dpkg and apt-cache in the chrooted environment.
    """

    # Initialize the output writer for packages content generation
    self.output_writer.initialize(Key.PACKAGES.value)

    # Generate the dpkg command to retrieve the list of installed packages
    command = "LANG=C chroot " + self.project.get_rootfs_mountpoint()
    command += " dpkg -l | tail -n +6"
    command_output = self.execute_command(command)

    # Iterate the output of the dpkg process:
    for binaryline in command_output.splitlines():
      # Each fields is stored into a variable to easy manipulation and
      # simplify code. First get the array of words converted to UTF-8
      line = binaryline.decode(Key.UTF8.value).split()

      # Extract each fields
      pkg_status = line[0]
      pkg_name = line[1]
      pkg_version = line[2]
      pkg_arch = line[3]

      # Space is used as a separator to rebuild the description
      pkg_description = " ".join(line[4:])

      # Initialize and empty dictionnaries. It is use to stores the key/value
      # pair used processed during output
      output_item = dict()

      # Test if we have to generate the package status in the output
      if Key.OUTPUT_PKG_STATUS.value in self.project.list_content[Key.PACKAGES.value]:
        if self.project.list_content[Key.PACKAGES.value][Key.OUTPUT_PKG_STATUS.value]:
          output_item[Key.STATUS.value] = pkg_status

      # Test if we have to generate the package name in the output
      if Key.OUTPUT_PKG_NAME.value in self.project.list_content[Key.PACKAGES.value]:
        if self.project.list_content[Key.PACKAGES.value][Key.OUTPUT_PKG_NAME.value]:
          output_item[Key.NAME.value] = pkg_name

      # Test if we have to generate the package version in the output
      if Key.OUTPUT_PKG_VERSION.value in self.project.list_content[Key.PACKAGES.value]:
        if self.project.list_content[Key.PACKAGES.value][Key.OUTPUT_PKG_VERSION.value]:
          output_item[Key.VERSION.value] = pkg_version

      # Test if we have to generate the package architecture in the output
      if Key.OUTPUT_PKG_ARCHITECTURE.value in \
                                          self.project.list_content[Key.PACKAGES.value]:
        if self.project.list_content[Key.PACKAGES.value]\
                                               [Key.OUTPUT_PKG_ARCHITECTURE.value]:
          output_item[Key.ARCHITECTURE.value] = pkg_arch

      # Test if we have to generate the package md5 in the output
      if Key.OUTPUT_PKG_MD5.value in self.project.list_content[Key.PACKAGES.value]:
        if self.project.list_content[Key.PACKAGES.value][Key.OUTPUT_PKG_MD5.value]:
          # Generate the apt-cache show command to retrieve the MD5sum
          # Grp the keyword and print second word
          command = "LANG=C chroot " + self.project.get_rootfs_mountpoint()
          command += " apt-cache show " + pkg_name + " | grep ^MD5sum | awk '{ print $2 }'"
          command_output = self.execute_command(command)
          output_item[Key.MD5.value] = command_output.decode(Key.UTF8.value)

      # Test if we have to generate the package sha256 in the output
      if Key.OUTPUT_PKG_SHA256.value in self.project.list_content[Key.PACKAGES.value]:
        if self.project.list_content[Key.PACKAGES.value][Key.OUTPUT_PKG_SHA256.value]:
          # Generate the apt-cache show command to retrieve the SHA256
          # Grp the keyword and print second word
          command = "LANG=C chroot " + self.project.get_rootfs_mountpoint()
          command += " apt-cache show " + pkg_name + " | grep ^SHA256 | awk '{ print $2 }'"
          command_output = self.execute_command(command)
          output_item[Key.SHA256.value] = command_output.decode(Key.UTF8.value)

      # Test if we have to generate the package size in the output
      if Key.OUTPUT_PKG_SIZE.value in self.project.list_content[Key.PACKAGES.value]:
        if self.project.list_content[Key.PACKAGES.value][Key.OUTPUT_PKG_SIZE.value]:
          # Generate the apt-cache show command to retrieve the Size
          # Grp the keyword and print second word
          command = "LANG=C chroot " + self.project.get_rootfs_mountpoint()
          command += " apt-cache show " + pkg_name + " | grep ^Size | awk '{ print $2 }'"
          command_output = self.execute_command(command)
          output_item[Key.SIZE.value] = command_output.decode(Key.UTF8.value)

      # Test if we have to generate the package installed-size in the output
      if Key.OUTPUT_PKG_INSTALLED_SIZE.value in \
                                          self.project.list_content[Key.PACKAGES.value]:
        if self.project.list_content[Key.PACKAGES.value]\
                                               [Key.OUTPUT_PKG_INSTALLED_SIZE.value]:
          # Generate the apt-cache show command to retrieve the Installed-SizeMD5sum
          # Grp the keyword and print second word
          command = "LANG=C chroot " + self.project.get_rootfs_mountpoint()
          command += " apt-cache show " + pkg_name
          command += " | grep ^Installed-Size | awk '{ print $2 }'"
          command_output = self.execute_command(command)
          output_item[Key.INSTALLED_SIZE.value] = command_output.decode(Key.UTF8.value)

      # Test if we have to generate the package description in the output
      if Key.OUTPUT_PKG_DESCRIPTION.value in \
                                          self.project.list_content[Key.PACKAGES.value]:
        if self.project.list_content[Key.PACKAGES.value]\
                                               [Key.OUTPUT_PKG_DESCRIPTION.value]:
          output_item[Key.DESCRIPTION.value] = pkg_description

      # print(output)
      self.output_writer.append_item(output_item)

    # Flush all pending output and close stream or file
    self.output_writer.flush_and_close()



  # -------------------------------------------------------------------------
  #
  # gen_files_info
  #
  # -------------------------------------------------------------------------
  def gen_files_info(self):
    """This method implement the generation of information about files.
    Informationare extracted from the host information, not the chroot.
    """

    # Initialize the output writer for packages content generation
    self.output_writer.initialize(Key.FILES.value)

    # Flush all pending output and close stream or file
    self.output_writer.flush_and_close()



  # -------------------------------------------------------------------------
  #
  # gen_antivirus_info
  #
  # -------------------------------------------------------------------------
  def gen_antivirus_info(self):
    """This method implement the generation of information aboutanti-virus
    analysis. It relies on call to an antivirus in the chrooted environment.
    """

# TODO at the beginning of each method, generate add the globl check and goes deeper
# no need to recheck everything in each method. Call sould be ended before

    # We have to generate part of the command used to run the antivirus, depending
    # on the environment. It is called the antivus_cmd_prefix. It will be used
    # in the coming command.
    antivirus_cmd_version = ""
    antivirus_cmd_update = ""
    antivirus_cmd_scan = ""

    # Check if the antivirus should be run from the host or the target system
    # then generate the command for both version output and clamav execution.
    # So far only clamav is supported.
    use_host_av = True
    if Key.USE_HOST_AV.value in self.project.list_content[Key.ANTIVIRUS.value]:
      if not self.project.list_content[Key.ANTIVIRUS.value][Key.USE_HOST_AV.value]:
        use_host_av = False

    # Log which AV we are going to use
    logging.debug("Using host antivirus : " + str(use_host_av))

    # Now generation platform is identfied, we can generation the coommands
    if use_host_av:
      # Generate the version command
      antivirus_cmd_version = "LANG=C clamscan --version"

      # Generate the update command
      antivirus_cmd_update = "LANG=C freshclam"

      # Generate the scan command
      antivirus_cmd_scan = "LANG=C clamscan --infected --recursive "
      antivirus_cmd_scan += self.project.get_rootfs_mountpoint()
    else:
      # Generate the version command
      antivirus_cmd_version = "LANG=C chroot " + self.project.get_rootfs_mountpoint()
      antivirus_cmd_version += " clamscan --version"

      # Generate the update command
      antivirus_cmd_update = "LANG=C chroot " + self.project.get_rootfs_mountpoint()
      antivirus_cmd_update += " freshclam"

      # Generate the scan command
      antivirus_cmd_scan = "LANG=C chroot " + self.project.get_rootfs_mountpoint()
      antivirus_cmd_scan += " clamscan --infected --recursive /"

    # Log the generated commands
    logging.debug("Antivirus version command : " + antivirus_cmd_version)
    logging.debug("Antivirus update command  : " + antivirus_cmd_update)
    logging.debug("Antivirus scan command    : " + antivirus_cmd_scan)

    # Check if clamscan is installed in the chrooted environment
    need_to_remove_package = False
    if not use_host_av:
      if not os.path.isfile(self.project.get_rootfs_mountpoint() + "/usr/bin/clamscan"):
        need_to_remove_package = self.check_install_missing_package("clamav")

    # This is the case which we use the host antivirus
    else:
      # Check if antivirus is present on the host. If not, nothin
      if not os.path.isfile("/usr/bin/clamscan"):
        logging.error("Clamav is missing and installation not allowed on host (only on target).")
        logging.error("Please consider to install it or switch to target execution")
        logging.critical("Generation cannot continue, execution is aborted.")
        exit(1)

    #
    # Checking and installation section is done. Now execute thee antivirus
    #

    # Initialize and empty dictionnaries. It is use to stores the key/value
    # pair used processed during output
    output_item = dict()

    # Initialize the output writer for packages content generation
    self.output_writer.initialize(Key.ANTIVIRUS.value)

    # Check if the database update is authorized by configuration (can be off for offline systems)
    if Key.UPDATE_DATABASE.value not in self.project.list_content[Key.ANTIVIRUS.value]:
      self.project.list_content[Key.ANTIVIRUS.value][Key.UPDATE_DATABASE.value] = True

    # Check if we have to update the database. Default is True. But it can be switched to False
    # for offline systems
    if self.project.list_content[Key.ANTIVIRUS.value][Key.UPDATE_DATABASE.value]:
      logging.debug("Starting to update Clamav database")
      command_output = self.execute_command(antivirus_cmd_update)

      # Parse the results and add lines to the output buffer
      for binaryline in command_output.splitlines():
        # Each fields is stored into a variable to easy manipulation and
        # simplify code. First get the array of words converted to UTF-8
        line = binaryline.decode(Key.UTF8.value)
        print(line)

        # Test if we have to generate the package status in the output
        output_item[Key.UPDATE_DATABASE.value] += line

    # Just output de debug log when deactivated
    else:
      logging.debug("Clamav database update is deactivated")

    # Generate the dpkg command to retrieve the list of installed packages
    logging.debug("Starting Clamav version command")
    command_output = self.execute_command(antivirus_cmd_version)
    output_item[Key.VERSION.value] = command_output.decode(Key.UTF8.value)

    # Generate the dpkg command to retrieve the list of installed packages
    logging.debug("Starting Clamav scan")
    command_output = self.execute_command(antivirus_cmd_scan)
    output_item[Key.SCAN.value] = command_output.decode(Key.UTF8.value)

    # print(output)
    self.output_writer.append_item(output_item)

    # Flush all pending output and close stream or file
    self.output_writer.flush_and_close()

    # Remove ClamAV if it has been installled in the chrooted environnement
    if need_to_remove_package:
      logging.debug("Starting to remove Clamav")
      self.remove_package("clamav")



  # -------------------------------------------------------------------------
  #
  # gen_security_info
  #
  # -------------------------------------------------------------------------
  def gen_security_info(self):
    """This method implement the generation of information about security.
    It relies on call to openscap or lynis in the chrooted environment.
    """

    # TODO need purge ?

    # Initialize the output writer for security content generation
    self.output_writer.initialize(Key.SECURITY.value)

    # Initialize and empty dictionnaries. It is use to stores the key/value
    # pair used processed during output
    output_item = dict()

    # Check if package is installed in the chrooted environment
    need_to_remove_package = False
    if not os.path.isfile(self.project.get_rootfs_mountpoint() + "/usr/sbin/lynis"):
      # Install missing packages into the chroot
      # Set the flag used tomark that we install debsecan and we have to
      # remove it before exiting the application
      need_to_remove_package = self.check_install_missing_package(Key.LYNIS.value)

    # Generate the debsecan execution command
    command = "chroot " + self.project.get_rootfs_mountpoint()
    command += " /usr/sbin/lynis audit system"
    command_output = self.execute_command(command)
    output_item[Key.LYNIS.value] = command_output.decode(Key.UTF8.value)

    # print(output)
    self.output_writer.append_item(output_item)

    # Test if debsecan has to be removed
    if need_to_remove_package:
      # Remove extra packages into the chroot
      logging.info("Removing lynis in rootfs")
      self.remove_package(Key.LYNIS.value)

    # Flush all pending output and close stream or file
    self.output_writer.flush_and_close()

    # Flush all pending output and close stream or file
    self.output_writer.flush_and_close()



  # -------------------------------------------------------------------------
  #
  # gen_rootkit_info
  #
  # -------------------------------------------------------------------------
  def gen_rootkit_info(self):
    """This method implement the execution of a rootkit scanner on the
    generated rootfs. It is based on the use of rkhunter in the chrooted
    environment.
    """

    # Initialize the output writer for rootkit content generation
    self.output_writer.initialize(Key.ROOTKIT.value)

    # Initialize and empty dictionnaries. It is use to stores the key/value
    # pair used processed during output
    output_item = dict()

    # Check if package is installed in the chrooted environment
    need_to_remove_package = False
    if not os.path.isfile(self.project.get_rootfs_mountpoint() + "/usr/bin/rkhunter"):
      # Install missing packages into the chroot
      # Set the flag used tomark that we install debsecan and we have to
      # remove it before exiting the application
      need_to_remove_package = self.check_install_missing_package(Key.RKHUNTER.value)

    # Generate the debsecan execution command
    command = "chroot " + self.project.get_rootfs_mountpoint()
    command += " /usr/bin/rkhunter --check --skip-keypress"
    command_output = self.execute_command(command)
    output_item[Key.RKHUNTER.value] = command_output.decode(Key.UTF8.value)

    # print(output)
    self.output_writer.append_item(output_item)

    # Test if debsecan has to be removed
    if need_to_remove_package:
      # Remove extra packages into the chroot
      logging.info("Removing rkhunter in rootfs")
      self.remove_package(Key.RKHUNTER.value)

    # Flush all pending output and close stream or file
    self.output_writer.flush_and_close()



  # -------------------------------------------------------------------------
  #
  # gen_vulnerabilities_info
  #
  # -------------------------------------------------------------------------
  def gen_vulnerabilities_info(self):
    """This method implement the generation of information about
    vulnerabilities. It relies on call to debsecan and apt-cache in the
    chrooted environment.
    """

     # Initialize the output writer for vulnerabilities content generation
    self.output_writer.initialize(Key.VULNERABILITIES.value)

    # Initialize and empty dictionnaries. It is use to stores the key/value
    # pair used processed during output
    output_item = dict()

    # Check if debsecan is installed in the chrooted environment
    need_to_remove_package = False
    if not os.path.isfile(self.project.get_rootfs_mountpoint() + "/usr/bin/debsecan"):
      # Install missing packages into the chroot
      # Set the flag used tomark that we install debsecan and we have to
      # remove it before exiting the application
      need_to_remove_package = self.check_install_missing_package("debsecan")

    # Generate the debsecan execution command
    command = "chroot " + self.project.get_rootfs_mountpoint()
    command += " /usr/bin/debsecan"
    command_output = self.execute_command(command)
    output_item["debsecan"] = command_output.decode(Key.UTF8.value)

    # Test if debsecan has to be removed
    if need_to_remove_package:
      # Remove extra packages into the chroot
      logging.info("Removing debsecan in rootfs")
      self.remove_package("debsecan")

    # Flush all pending output and close stream or file
    self.output_writer.flush_and_close()

#TODO does seems to output anything



  # -------------------------------------------------------------------------
  #
  # check_install_missing_package
  #
  # -------------------------------------------------------------------------
  def check_install_missing_package(self, packages):
    """This method implement the logic of missing packages instalaltion in
    the rootfs. Some operation may neeed packages which are not in the rootfs,
    thus     we may have to install these packages to execute the command.

    The method checks project configuration for the possibility to install
    missing packages. If installation is authorized, the it install it and
    return True ( meaning need to remove packages avec execution), otherwise
    it returns false or exit if skipping on error is not authorized.
    """

    # If install_missing_software key is not defined, then set its default value
    if Key.INSTALL_MISSING_SOFTWARE.value not in \
                                    self.project.list_content[Key.CONFIGURATION.value]:
      self.project.list_content[Key.CONFIGURATION.value]\
                                          [Key.INSTALL_MISSING_SOFTWARE.value] = False

    # If skip_missing_software key is not defined, then set its default value
    if Key.SKIP_MISSING_SOFTWARE.value not in \
                                    self.project.list_content[Key.CONFIGURATION.value]:
      logging.debug("Setting default value of skip_missing_software to False")
      self.project.list_content[Key.CONFIGURATION.value]\
                                          [Key.SKIP_MISSING_SOFTWARE.value] = True

    # Check if installation is authorized sinc the software is missing
    if self.project.list_content[Key.CONFIGURATION.value]\
                                           [Key.INSTALL_MISSING_SOFTWARE.value]:
      logging.info("Installing " + packages + " in rootfs")

      # Update the catalog before installing
      if self.project.list_content[Key.CONFIGURATION.value]\
                                             ["update_catalog_before_install"]:
        self.update_package_catalog()

      # Install missing packages into the chroot
      self.install_package(packages)

      # Set the flag used tomark that we install clamav and we have to
      # remove it before exiting the application
      return True

    # Not installed and not allowed to install missing software
    else:
      # Check if skipping is allowed or not
      if self.project.list_content[Key.CONFIGURATION.value]\
                                             [Key.SKIP_MISSING_SOFTWARE.value]:
        logging.warning("Skipping vulnerabilities content generation. Clamav is missing\
                        and installation not allowed by configuration file.")
        return False
      else:
        # Skipping is deactivated, so is installation, thus it fails
        logging.error("Clamav is missing and installation not allowed by configuration file.")
        logging.error("Please consider to add skip_missing_software or \
                      install_mising_software in configuration file")
        logging.critical("Generation cannot continue, execution is aborted.")
        exit(1)
