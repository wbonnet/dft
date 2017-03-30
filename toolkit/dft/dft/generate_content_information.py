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
from cli_command import CliCommand

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
    self.output_buffer = list()

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
  # flush_and_close
  #
  # -------------------------------------------------------------------------
  def flush_and_close(self):
    """This method is in charg of flushing all the output and close opened
    files
    """

    print(self.output_buffer)

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
    self.output_writer = ContentOutputWriter(self.project.content_information_def)



  # -------------------------------------------------------------------------
  #
  # gen_content_info
  #
  # -------------------------------------------------------------------------
  def gen_content_info(self):
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
    if self.project.content_information_def is None:
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
      if "packages" in self.project.content_information_def:
        logging.debug("Packages information generation is activated")
        self.gen_packages_info()
      else:
        logging.info("Packages information generation is deactivated")

    #
    # Generate the vulnerabilities information
    #
    if self.project.dft.generate_all_information or self.project.dft.gen_vulnerabilities_info:
      if "vulnerabilities" in self.project.content_information_def:
        logging.debug("Vulnerabilities information generation is activated")
        self.gen_vulnerabilities_info()
      else:
        logging.info("Vulnerabilities information generation is deactivated")

    #
    # Generate the security information
    #
    if self.project.dft.generate_all_information or self.project.dft.gen_security_info:
      if "security" in self.project.content_information_def:
        logging.debug("Security information generation is activated")
        self.gen_security_info()
      else:
        logging.info("Security information generation is deactivated")

    #
    # Generate the files information
    #
    if self.project.dft.generate_all_information or self.project.dft.gen_files_info:
      if "files" in self.project.content_information_def:
        logging.debug("File information generation is activated")
        self.gen_files_info()
      else:
        logging.info("Files information generation is deactivated")

    #
    # Generate the anti-virus information
    #
    if self.project.dft.generate_all_information or self.project.dft.gen_antivirus_info:
      if "antivirus" in self.project.content_information_def:
        logging.debug("Anti-virus information generation is activated")
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
    self.output_writer.initialize("packages")

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

      # Space is used as a separator to rebuild the description
      pkg_description = " ".join(line[4:])

      # Initialize and empty dictionnaries. It is use to stores the key/value
      # pair used processed during output
      output_item = dict()

      # Test if we have to generate the package status in the output
      if "output_pkg_status" in self.project.content_information_def["packages"]:
        if self.project.content_information_def["packages"]["output_pkg_status"]:
          output_item["status"] = pkg_status

      # Test if we have to generate the package name in the output
      if "output_pkg_name" in self.project.content_information_def["packages"]:
        if self.project.content_information_def["packages"]["output_pkg_name"]:
          output_item["name"] = pkg_name

      # Test if we have to generate the package version in the output
      if "output_pkg_version" in self.project.content_information_def["packages"]:
        if self.project.content_information_def["packages"]["output_pkg_version"]:
          output_item["version"] = pkg_version

      # Test if we have to generate the package architecture in the output
      if "output_pkg_architecture" in self.project.content_information_def["packages"]:
        if self.project.content_information_def["packages"]["output_pkg_architecture"]:
          output_item["architecture"] = pkg_arch

      # Test if we have to generate the package md5 in the output
      if "output_pkg_md5" in self.project.content_information_def["packages"]:
        if self.project.content_information_def["packages"]["output_pkg_md5"]:
          # Generate the apt-cache show command to retrieve the MD5sum
          # Grp the keyword and print second word
          sudo_command = "LANG=C sudo chroot " + self.project.rootfs_mountpoint
          sudo_command += " apt-cache show " + pkg_name + " | grep ^MD5sum | awk '{ print $2 }'"
          sudo_command_output = self.execute_command(sudo_command)
          output_item["md5"] = sudo_command_output.decode('utf-8')

      # Test if we have to generate the package sha256 in the output
      if "output_pkg_sha256" in self.project.content_information_def["packages"]:
        if self.project.content_information_def["packages"]["output_pkg_sha256"]:
          # Generate the apt-cache show command to retrieve the SHA256
          # Grp the keyword and print second word
          sudo_command = "LANG=C sudo chroot " + self.project.rootfs_mountpoint
          sudo_command += " apt-cache show " + pkg_name + " | grep ^SHA256 | awk '{ print $2 }'"
          sudo_command_output = self.execute_command(sudo_command)
          output_item["sha256"] = sudo_command_output.decode('utf-8')

      # Test if we have to generate the package size in the output
      if "output_pkg_size" in self.project.content_information_def["packages"]:
        if self.project.content_information_def["packages"]["output_pkg_size"]:
          # Generate the apt-cache show command to retrieve the Size
          # Grp the keyword and print second word
          sudo_command = "LANG=C sudo chroot " + self.project.rootfs_mountpoint
          sudo_command += " apt-cache show " + pkg_name + " | grep ^Size | awk '{ print $2 }'"
          sudo_command_output = self.execute_command(sudo_command)
          output_item["size"] = sudo_command_output.decode('utf-8')

      # Test if we have to generate the package installed-size in the output
      if "output_pkg_installed_size" in self.project.content_information_def["packages"]:
        if self.project.content_information_def["packages"]["output_pkg_installed_size"]:
          # Generate the apt-cache show command to retrieve the Installed-SizeMD5sum
          # Grp the keyword and print second word
          sudo_command = "LANG=C sudo chroot " + self.project.rootfs_mountpoint
          sudo_command += " apt-cache show " + pkg_name
          sudo_command += " | grep ^Installed-Size | awk '{ print $2 }'"
          sudo_command_output = self.execute_command(sudo_command)
          output_item["installed-size"] = sudo_command_output.decode('utf-8')

      # Test if we have to generate the package description in the output
      if "output_pkg_description" in self.project.content_information_def["packages"]:
        if self.project.content_information_def["packages"]["output_pkg_description"]:
          output_item["description"] = pkg_description

      # print(output)
      self.output_writer.output_buffer.append(output_item)

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
    self.output_writer.initialize("files")

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
    # in the coming sudo command.
    antivirus_cmd_version = ""
    antivirus_cmd_update = ""
    antivirus_cmd_scan = ""

    # Check if the antivirus should be run from the host or the target system
    # then generate the command for both version output and clamav execution.
    # So far only clamav is supported.
    use_host_av = True
    if "use_host_av" in self.project.content_information_def["antivirus"]:
      if not self.project.content_information_def["antivirus"]["use_host_av"]:
        use_host_av = False

    # Log which AV we are going to use
    logging.debug("Using host antivirus : " + str(use_host_av))

    # Now generation platform is identfied, we can generation the coommands
    if use_host_av:
      # Generate the version command
      antivirus_cmd_version = "LANG=C sudo clamscan --version"

      # Generate the update command
      antivirus_cmd_update = "LANG=C sudo freshclam"

      # Generate the scan command
      antivirus_cmd_scan = "LANG=C sudo clamscan --infected --recursive "
      antivirus_cmd_scan += self.project.rootfs_mountpoint
    else:
      # Generate the version command
      antivirus_cmd_version = "LANG=C sudo chroot " + self.project.rootfs_mountpoint
      antivirus_cmd_version += " clamscan --version"

      # Generate the update command
      antivirus_cmd_update = "LANG=C sudo chroot " + self.project.rootfs_mountpoint
      antivirus_cmd_update += " freshclam"

      # Generate the scan command
      antivirus_cmd_scan = "LANG=C sudo chroot " + self.project.rootfs_mountpoint
      antivirus_cmd_scan += " clamscan --infected --recursive /"

    # Log the generated commands
    logging.debug("Antivirus version command : " + antivirus_cmd_version)
    logging.debug("Antivirus update command  : " + antivirus_cmd_update)
    logging.debug("Antivirus scan command    : " + antivirus_cmd_scan)

    # Check if clamscan is installed in the chrooted environment
    need_to_remove_clamav = False
    if not use_host_av:
      if not os.path.isfile(self.project.rootfs_mountpoint + "/usr/bin/clamscan"):
        # If not, test if it has to be installed, or should it fail ?
        # Default behavior is to install clamav if missing and to remove
        # it if it has been installed in this method context (and not in the
        # rootfs)

        # If install_missing_software key is not defined, then set its default value
        if "install_missing_software" not in self.project.content_information_def["configuration"]:
          self.project.content_information_def["configuration"]["install_missing_software"] = False

        # If skip_missing_software key is not defined, then set its default value
        if "skip_missing_software" not in self.project.content_information_def["configuration"]:
          logging.debug("Setting default value of skip_missing_software to False")
          self.project.content_information_def["configuration"]["skip_missing_software"] = True

        # Check if installation is authorized sinc the software is missing
        if self.project.content_information_def["configuration"]["install_missing_software"]:
          logging.info("Installing clamav in rootfs")

          # Update the catalog before installing
          sudo_command = "sudo chroot " + self.project.rootfs_mountpoint
          sudo_command += " /usr/bin/apt-get update --allow-unauthenticated"
          self.execute_command(sudo_command)

          # Install missing packages into the chroot
          sudo_command = "sudo chroot " + self.project.rootfs_mountpoint
          sudo_command += " /usr/bin/apt-get install --no-install-recommends"
          sudo_command += " --yes --allow-unauthenticated clamav"
          self.execute_command(sudo_command)
#TODO remove and purge it after execution

          # Set the flag used tomark that we install clamav and we have to
          # remove it before exiting the application
          need_to_remove_clamav = True

        # Not installed and not allowed to install missing software
        else:
          # Check if skipping is allowed or not
          if self.project.content_information_def["configuration"]["skip_missing_software"]:
            logging.warning("Skipping vulnerabilities content generation. Clamav is missing\
                            and instalation not allowed by configuration file.")
            return
          else:
            # Skipping is deactivated, so is installation, thus it fails
            logging.error("Clamav is missing and installation not allowed by configuration file.")
            logging.error("Please consider to add skip_missing_software or \
                          install_mising_software in configuration file")
            logging.critical("Generation cannot continue, execution is aborted.")
            exit(1)
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
    self.output_writer.initialize("antivirus")

    # Check if the database update is authorized by configuration (can be off for offline systems)
    if "update_database" not in self.project.content_information_def["antivirus"]:
      self.project.content_information_def["antivirus"]["update_database"] = True

    # Check if we have to update the database. Default is True. But it can be switched to False
    # for offline systems
    if self.project.content_information_def["antivirus"]["update_database"]:
      logging.debug("Starting to update Clamav database")
      sudo_command_output = self.execute_command(antivirus_cmd_update)

      # Parse the results and add lines to the output buffer
      for binaryline in sudo_command_output.splitlines():
        # Each fields is stored into a variable to easy manipulation and
        # simplify code. First get the array of words converted to UTF-8
        line = binaryline.decode('utf-8')
        print(line)

        # Test if we have to generate the package status in the output
        output_item["update database"] += line

    # Just output de debug log when deactivated
    else:
      logging.debug("Clamav database update is deactivated")

    # Generate the dpkg command to retrieve the list of installed packages
    logging.debug("Starting Clamav version command")
    sudo_command_output = self.execute_command(antivirus_cmd_version)
    output_item["version"] = sudo_command_output.decode('UTF-8')

    # Generate the dpkg command to retrieve the list of installed packages
    logging.debug("Starting Clamav scan")
    sudo_command_output = self.execute_command(antivirus_cmd_scan)
    output_item["scan"] = sudo_command_output.decode('UTF-8')

    # print(output)
    self.output_writer.output_buffer.append(output_item)

    # Flush all pending output and close stream or file
    self.output_writer.flush_and_close()

    # Remove ClamAV if it has been installled in the chroooted environnement
    if need_to_remove_clamav:
      logging.debug("Starting to remove Clamav")
      self.remove_package("clamav")



  # -------------------------------------------------------------------------
  #
  # gen_security_info
  #
  # -------------------------------------------------------------------------
  def gen_security_info(self):
    """This method implement the generation of information about security.
    It relies on call to openscap in the chrooted environment.
    """

    # TODO need purge ?

    # Initialize the output writer for packages content generation
    self.output_writer.initialize("security")

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

     # Initialize the output writer for packages content generation
    self.output_writer.initialize("vulnerabilities")

    # Check if debsecan is installed in the chrooted environment
    if not os.path.isfile(self.project.rootfs_mountpoint + "/usr/bin/debsecan"):
      # If not, test if it has to be installed, or should it fail ?
      # Default behavior is to install debsecan if missing and to remove
      # it if it has been installed in this method context (and not in the
      # rootfs)
      # If key is not defined, then set its default value
      if self.project.content_information_def["configuration"] != None:
        if "install_missing_software" not in self.project.content_information_def["configuration"]:
          logging.debug("Setting default value of install_missing_software to False")
          self.project.content_information_def["configuration"]["install_missing_software"] = False
      else:
        logging.debug("Setting default value of install-missing-software to False")
        self.project.content_information_def["configuration"] = {'install_missing_software': False}

      if self.project.content_information_def["configuration"]["install_missing_software"]:
        logging.info("Installing debsecan in rootfs")

        # Install missing packages into the chroot
        self.install_package("debsecan")

        # Set the flag used tomark that we install debsecan and we have to
        # remove it before exiting the application
        need_to_remove_debsecan = True

      # The tool is missing and installation is not allowed,thus either we
      # allowed to skip this stage, or we fail and exit
      else:
        # If key is not defined, then set its default value
        if self.project.content_information_def["configuration"] != None:
          if "skip_missing_software" not in self.project.content_information_def["configuration"]:
            logging.debug("Setting default value of skip_missing_software to False")
            self.project.content_information_def["configuration"]["skip_missing_software"] = True
        else:
          logging.debug("Setting default value of skip_missing_software to False")
          self.project.content_information_def["configuration"] = {'skip_missing_software': True}

        # Check if skipping is allowed or not
        if self.project.content_information_def["configuration"]["skip_missing_software"]:
          logging.warning("Skipping vulnerabilities content generation. Debsecan is missing and \
                          instalation not allowed by configuration file.")
          return
        else:
          # Skipping is deactivated, so is installation, thus it fails
          logging.error("Debsecan is missing and installation not allowed by configuration file.")
          logging.error("Please consider to add skip_missing_software or \
                        install_mising_software in configuration file")
          logging.critical("Generation cannot continue, execution is aborted.")
          exit(1)

    # Generate the debsecan execution command
    sudo_command = "sudo chroot " + self.project.rootfs_mountpoint
    sudo_command += " /usr/bin/debsecan"
    self.execute_command(sudo_command)

    # Test if debsecan has to be removed
    if need_to_remove_debsecan:
      logging.info("Removing debsecan in rootfs")

      # Remove extra packages into the chroot
      self.remove_package("debsecan")

    # Flush all pending output and close stream or file
    self.output_writer.flush_and_close()
