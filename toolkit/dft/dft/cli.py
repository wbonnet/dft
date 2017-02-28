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

""" This module contains the class and method used to crate parsers dedicated to the
different words of command supported by DFT.

The module will do actual processing and run the associated worker method (run method)
"""

import argparse
import textwrap
import logging
import build_baseos
import model
import assemble_firmware
import build_bootloader
import build_image
import build_firmware
import check_rootfs
import generate_content_information
import strip_rootfs

# -----------------------------------------------------------------------------
#
#  Class Cli
#
# -----------------------------------------------------------------------------
class Cli(object):
  """This class represent the command line parser for this tool. It brings
  methods used to parse command line arguments then run the program itself
  """

  # -------------------------------------------------------------------------
  #
  # __init__
  #
  # -------------------------------------------------------------------------
  def __init__(self):
    # Current version
    self.version = "0.1.0"

    # Create the internal parser from argparse
    self.parser = argparse.ArgumentParser(description=textwrap.dedent('''\
Debian Firmware Toolkit v''' + self.version + '''

DFT is a collection of tools used to create Debian based firmwares 
                  
Available commands are :
? assemble_firmware                Create a firmware from a baseos and generate the configuration files used to loading after booting
. build_baseos                     Generate a debootstrap from a Debian repository, install and configure required packages
? build_bootloader                 Build the bootloader toolchain (kernel, initramfs, grub or uboot)
? build_image                      Build the disk image from the firmware (or rootfs) and bootloader toolchain
. build_firmware                   Build the firmware configuration files and scripts used to load in memory the firmware
. check_rootfs                     Control the content of the baseos rootfs after its generation (debsecan and openscap)
x factory_setup                    Apply some extra factory setup before generating the firmware
? generate_content_information     Generate a manifest identiyfing content and versions
? strip_rootfs                     Strip down the rootfs before assembling the firmware'''),
                                          formatter_class=argparse.RawTextHelpFormatter)

    # Storesthe arguments from the parser
    self.args = None

    # Stores the argument in the instance
    self.command = None

    # Stores the dft configuration object
    self.dft = None

    # Stores the project definition object
    self.project = None


  def parse(self, args):
    # Stores the argument in the instance
    self.command = args

    self.add_parser_option_common()
# TODO command build project

    # According to the command, call the method dedicated to parse the arguments
    if   self.command == "assemble_firmware":
      self.add_parser_option_assemble_firmware()
    elif self.command == "build_baseos":
      self.add_parser_option_build_baseos()
    elif self.command == "build_bootloader":
      self.add_parser_option_build_bootloader()
    elif self.command == "build_image":
      self.add_parser_option_build_image()
    elif self.command == "build_firmware":
      self.add_parser_option_build_firmware()
    elif self.command == "check_rootfs":
      self.add_parser_option_check_rootfs()
    elif self.command == "factory_setup":
      self.add_parser_option_factory_setup()
    elif self.command == "generate_content_information":
      self.add_parser_option_generate_content_information()
    elif self.command == "strip_rootfs":
      self.add_parser_option_strip_rootfs()
    else:
      # If the command word is unknown, the force the parsing of the help flag
      return self.parser.parse_args(['-h'])

    # Finally call the parser that has been completed by the previous lines
    self.args = self.parser.parse_args()

  def add_parser_option_assemble_firmware(self):
    # Add the arguments
    self.parser.add_argument('assemble_firmware',
                             help='Command to execute')


  def add_parser_option_build_baseos(self):
    # Add the arguments
    self.parser.add_argument('build_baseos',
                             help='Command to execute')

    # Overrides the target architecture from the configuration file by
    # limiting it to a given list of arch. Architectures not defined in
    # the configuration file can be added with this parameter
# TODO: parse the list of argument. So far only one value is handled
    self.parser.add_argument('--limit-arch',
                             action='store',
                             dest='limit_target_arch',
                             help='limit the list of target arch to process (comma separated list of arch eg: arch1,arch2)')

    # Overrides the target version used to build the baseos. Version to
    # use is limited it to a given list of arch. Versions not defined
    # in the configuration file can be added with this parameter
# TODO: parse the list of argument. So far only one value is handled
    self.parser.add_argument('--limit-version',
                             action='store',
                             dest='limit_target_version',
                             help='limit the list of target version to process (comma separated list of versions eg: jessie,stretch)')

    # Activate the use of the rootfs cache archive. When building a baseos
    # with debootstrap, having this option enable will make DFT look for
    # an existing cache archive, an extract it instead of doing a fresh
    # debootstrap installation
    self.parser.add_argument('--use-cache-archive',
                             action='store_true',
                             dest='use_cache_archive',
                             help="activate the use of an existing cache archive (extract archive instead of running debootstrap). \n"
                             "This option does nothing if the cache archive do no exist. In this case, debootstrap will be \n"
                             "launched and the missing archive will not be created")

    # Activate the use of the rootfs cache archive. When building a baseos
    # with debootstrap, having this option enable will make DFT look for
    # an existing cache archive, an extract it instead of doing a fresh
    # debootstrap installation
    self.parser.add_argument('--update-cache-archive',
                             action='store_true',
                             dest='update_cache_archive',
                             help="update the cache archive after building a baseos with debootstrap. Existing archive will\n"
                             "be deleted if it already exist, or it will be created if missing")

    # Override the list of mirrors defined in the configuration file.
    # This option defines a single mirror, not a full list of mirrors.
    # Thus the list of mirrors will be replaced by a single one
    self.parser.add_argument('--override-debian-mirror',
                             action='store',
                             dest='override_debian_mirror',
                             help="override the list of mirrors defined in the configuration file. This option\n"
                             "defines a single mirror, not a full list of mirrors. Thus the list of mirrors\n"
                             "will be replaced by a single one")

    # During installation ansible files from DFT toolkit are copied to
    # /dft_bootstrap in the target rootfs. This option prevents DFT from
    # removing these files. This is useful to debug ansible stuff and
    # replay an playbooks at will
    self.parser.add_argument('--keep-bootstrap-files',
                             action='store_true',
                             dest='keep_bootstrap_files',
                             help='do not delete DFT bootstrap files after installation (debug purpose)')



  def add_parser_option_build_bootloader(self):
    # Add the arguments
    self.parser.add_argument('build_bootloader',
                             help='Command to execute')



  def add_parser_option_build_image(self):    # Add the arguments
    # Add the arguments
    self.parser.add_argument('build_image',
                             help='Command to execute')



  def add_parser_option_build_firmware(self):
    # Add the arguments
    self.parser.add_argument('build_firmware',
                             help='Command to execute')



  def add_parser_option_check_rootfs(self):
    # Add the arguments
    self.parser.add_argument('build_check_rootfs',
                             help='Command to execute')



  def add_parser_option_factory_setup(self):
    # Add the arguments
    self.parser.add_argument('factory_setup',
                             help='Command to execute')



  def add_parser_option_generate_content_information(self):
    # Add the arguments
    self.parser.add_argument('generate_content_information',
                             help='Command to execute')

    # Activate the generation of the packages information.
    # Default behavior is to generate everything if no generate_xxx_information
    # flag is set. If at least one fag is set, then the user has to set every
    # needed flag
    self.parser.add_argument('--generate-packages-information',
                             action='store_true',
                             dest='generate_packages_information',
                             help="generate the information about packages. If at least one of the\n"
                             "generate_something_information is set,then it deactivatethe 'generate all'\n"
                             "default behavior, and each information source has to be set.\n")

    # Activate the generation of information about vulnerabilities
    self.parser.add_argument('--generate-vulnerabilities-information',
                             action='store_true',
                             dest='generate_vulnerabilities_information',
                             help="generate the information about vulnerabilities.\n")

    # Activate the generation of information about security
    self.parser.add_argument('--generate-security-information',
                             action='store_true',
                             dest='generate_security_information',
                             help="generate the information about security.\n")

    # Activate the generation of information about files.
    self.parser.add_argument('--generate-files-information',
                             action='store_true',
                             dest='generate_files_information',
                             help="generate the information about files.\n")

    # Activate the generation of information about the anti-virus execution.
    self.parser.add_argument('--generate-antivirus-information',
                             action='store_true',
                             dest='generate_antivirus_information',
                             help="generate the information about anti-virus execution.\n")



  def add_parser_option_strip_rootfs(self):
    # Add the arguments
    self.parser.add_argument('strip_rootfs',
                             help='Command to execute')



  def add_parser_option_common(self):
    # Configuration file store the definition of baseos. Optioncan be
    # overriden by arguments on the command line (like --target-arch)
    #
    # Configuration file defines baseos and its modulation
    self.parser.add_argument('--config-file',
                             action='store',
                             dest='config_file',
                             default='dft.yml',
                             help='DFT configuration file')

    # Project definition file defines environnement shared between
    # the different DFT commands (such as path to diirectory storing)
    # cache archives, temporary working dir, temp dir name patterns, etc.)
    self.parser.add_argument('--project-file',
                             action='store',
                             dest='project_file',
                             default='project.yml',
                             required=True,
                             help='project definition file')

    # Defines the level of the log to output
    self.parser.add_argument('--log-level',
                             action='store',
                             dest='log_level',
                             choices=['debug', 'info', 'warning', 'error', 'critical'],
                             help="defines the minimal log level. Default value is  warning")

  # -------------------------------------------------------------------------
  #
  # run
  #
  # -------------------------------------------------------------------------
  def run(self):
    """ According to the command, call the method dedicated to run the
      command called from cli
    """

    # Create the dft configuration object, and load its configuration
    self.dft = model.DftConfiguration(self.args.config_file)
# TODO    self.dft.load_configuration()

    # Create the project definition object, and load its configuration
    self.project = model.ProjectDefinition(self.args.project_file)
    self.project.load_definition()

    # ---------------------------------------------------------------------
    # Override configuration with values passed on the commande line

    # TODO : use a config file for log definition
    # Get the log_level from command line
    if self.args.log_level != None:
      self.project.dft.log_level = self.args.log_level.upper()
    # If not command line value, defaults to log
    else:
      self.project.dft.log_level = "INFO"

    # Create the logger object
    logging.basicConfig(level=self.project.dft.log_level)
    self.project.logging = logging.getLogger()

    # Get the config file from command line
    if self.args.config_file != None:
      self.project.logging.debug("Overriding config_file with CLI value : %s => %s",
                                 self.project.dft.configuration_file,
                                 self.args.config_file)
      self.project.dft.configuration_file = self.args.config_file

    # ---------------------------------------------------------------------

    # Select the method to run according to the command
    if self.command == "assemble_firmware":
      self.run_assemble_firmware()
    elif self.command == "build_baseos":
      self.run_build_baseos()
    elif self.command == "build_bootloader":
      self.run_build_bootloader()
    elif self.command == "build_image":
      self.run_build_image()
    elif self.command == "build_firmware":
      self.run_build_firmware()
    elif self.command == "check_rootfs":
      self.run_check_rootfs()
    elif self.command == "factory_setup":
      self.run_factory_setup()
    elif self.command == "generate_content_information":
      self.run_generate_content_information()
    elif self.command == "strip_rootfs":
      self.run_strip_rootfs()

  # -------------------------------------------------------------------------
  #
  # run_assemble_firmware
  #
  # -------------------------------------------------------------------------
  def run_assemble_firmware(self):
    """ Method used to handle the assemble_firmware command.
      Create the business objet, then execute the entry point
    """
    # Create the business object
    command = assemble_firmware.AssembleFirmware(self.dft, self.project)

    # Then
    command.assemble_firmware()



  # -------------------------------------------------------------------------
  #
  # run_build_baseos
  #
  # -------------------------------------------------------------------------
  def run_build_baseos(self):
    """ Method used to handle the build_baseos command.
      Create the business objet, then execute the entry point
    """

    # ---------------------------------------------------------------------
    # Override configuration with values passed on the commande line

    if self.args.keep_bootstrap_files != None:
      if self.args.keep_bootstrap_files != self.project.dft.keep_bootstrap_files:
        self.project.logging.debug("Overriding keep_bootstrap_files with CLI value : %s => %s",
                                   self.project.dft.keep_bootstrap_files,
                                   self.args.keep_bootstrap_files)
        self.project.dft.keep_bootstrap_files = self.args.keep_bootstrap_files

    if self.args.override_debian_mirror != None:
      if self.args.override_debian_mirror != self.project.project_definition["project-definition"]["debootstrap-repository"]:
        self.project.logging.debug("Overriding pkg_archive_url with CLI value : %s => %s",
                                   self.project.project_definition["project-definition"]["debootstrap-repository"],
                                   self.args.override_debian_mirror)
        self.project.project_definition["project-definition"]["debootstrap-repository"] = self.args.override_debian_mirror

    if self.args.update_cache_archive != None:
      if self.args.update_cache_archive != self.project.dft.update_cache_archive:
        self.project.logging.debug("Overriding update_cache_archive with CLI value : %s => %s",
                                   self.project.dft.update_cache_archive,
                                   self.args.update_cache_archive)
        self.project.dft.update_cache_archive = self.args.update_cache_archive

    if self.args.use_cache_archive != None:
      if self.args.use_cache_archive != self.project.dft.use_cache_archive:
        self.project.logging.debug("Overriding use_cache_archive with CLI value : %s => %s",
                                   self.project.dft.use_cache_archive,
                                   self.args.use_cache_archive)
        self.project.dft.use_cache_archive = self.args.use_cache_archive

    if self.args.limit_target_version != None:
      if self.args.limit_target_version != self.project.target_version:
        self.project.logging.debug("Overriding target_version with CLI value : %s => %s",
                                   self.project.target_version,
                                   self.args.limit_target_version)
        self.project.target_version = self.args.limit_target_version

    if self.args.limit_target_arch != None:
      if self.args.limit_target_arch != self.project.target_arch:
        self.project.logging.debug("Overriding target_arch with CLI value : %s => %s",
                                   self.project.target_arch,
                                   self.args.limit_target_arch)
        self.project.target_arch = self.args.limit_target_arch

    # Create the business object
    command = build_baseos.BuildBaseOS(self.dft, self.project)

    # Then
    command.install_baseos()



  # -------------------------------------------------------------------------
  #
  # run_build_bootloader
  #
  # -------------------------------------------------------------------------
  def run_build_bootloader(self):
    """ Method used to handle the build_bootloader command.
      Create the business objet, then execute the entry point
    """
    # Create the business object
    command = build_bootloader.BuildBootloader(self.dft, self.project)

    # Then
    command.build_bootloader()



  # -------------------------------------------------------------------------
  #
  # run_build_image
  #
  # -------------------------------------------------------------------------
  def run_build_image(self):
    """ Method used to handle the build_image command.
      Create the business objet, then execute the entry point
    """
    # Create the business object
    command = build_image.BuildImage(self.dft, self.project)

    # Then
    command.build_image()



  # -------------------------------------------------------------------------
  #
  # run_build_firmware
  #
  # -------------------------------------------------------------------------
  def run_build_firmware(self):
    """ Method used to handle the build_firmware command.
      Create the business objet, then execute the entry point
    """
    # Create the business object
    command = build_firmware.BuildFirmware(self.dft, self.project)

    # Then
    command.build_firmware()



  # -------------------------------------------------------------------------
  #
  # run_check_rootfs
  #
  # -------------------------------------------------------------------------
  def run_check_rootfs(self):
    """ Method used to handle the check_rootfs command.
      Create the business objet, then execute the entry point
    """
    # Create the business object
    command = check_rootfs.CheckRootFS(self.dft, self.project)

    # Then
    command.check_rootfs()



  # -------------------------------------------------------------------------
  #
  # run_factory_setup
  #
  # -------------------------------------------------------------------------
  def run_factory_setup(self):
    pass


  # -------------------------------------------------------------------------
  #
  # run_content_information
  #
  # -------------------------------------------------------------------------
  def run_generate_content_information(self):
    """ Method used to handle the generate_content_information command.
      Create the business objet, then execute the entry point
    """

    # Check if we have to do a 'generate all' or if some more specific flags
    # have ben set to reduce output. Default is generate all to true and all
    # other flags to false
    self.project.dft.generate_all_information = True
    self.project.dft.generate_packages_information = False
    self.project.dft.generate_files_information = False
    self.project.dft.generate_antivirus_information = False
    self.project.dft.generate_vulnerabilities_information = False
    self.project.dft.generate_security_information = False

    # Check if the packages are needed
    if self.args.generate_packages_information != None:
      # Flag is defined, then copy it
      self.project.dft.generate_packages_information = self.args.generate_packages_information
      # If flag is true, then generate all as to be false
      if self.project.dft.generate_packages_information:
        self.project.dft.generate_all_information = False

    # Check if the files are needed
    if self.args.generate_files_information != None:
      # Flag is defined, then copy it
      self.project.dft.generate_files_information = self.args.generate_files_information
      # If flag is true, then generate all as to be false
      if self.project.dft.generate_files_information:
        self.project.dft.generate_all_information = False

    # Check if the vulnerabilties are needed
    if self.args.generate_vulnerabilities_information != None:
      # Flag is defined, then copy it
      self.project.dft.generate_vulnerabilities_information = self.args.generate_vulnerabilities_information
      # If flag is true, then generate all as to be false
      if self.project.dft.generate_vulnerabilities_information:
        self.project.dft.generate_all_information = False

    # Check if the antivirus are needed
    if self.args.generate_antivirus_information != None:
      # Flag is defined, then copy it
      self.project.dft.generate_antivirus_information = self.args.generate_antivirus_information
      # If flag is true, then generate all as to be false
      if self.project.dft.generate_antivirus_information:
        self.project.dft.generate_all_information = False

    # Check if the security are needed
    if self.args.generate_security_information != None:
      # Flag is defined, then copy it
      self.project.dft.generate_security_information = self.args.generate_security_information
      # If flag is true, then generate all as to be false
      if self.project.dft.generate_security_information:
        self.project.dft.generate_all_information = False

    # Create the business object
    command = generate_content_information.GenerateContentInformation(self.dft, self.project)

    # Then
    command.generate_content_information()


  # -------------------------------------------------------------------------
  #
  # run_strip_rootfs
  #
  # -------------------------------------------------------------------------
  def run_strip_rootfs(self):
    """ Method used to handle the strip_rootfs command.
      Create the business objet, then execute the entry point
    """
    # Create the business object
    command = strip_rootfs.StripRootFS(self.dft, self.project)

    # Then
    command.strip_rootfs()
  