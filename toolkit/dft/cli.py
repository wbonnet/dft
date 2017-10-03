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
from dft import build_rootfs
from dft import model
from dft.model import Key
from dft import assemble_firmware
from dft import install_bootchain
from dft import build_image
from dft import build_firmware
from dft import check_rootfs
from dft import generate_content_information
from dft import strip_rootfs

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
    """Default constructor
    """

    # Current version
    self.version = "0.4.11"

    # Create the internal parser from argparse
    self.parser = argparse.ArgumentParser(description=textwrap.dedent('''\
Debian Firmware Toolkit v''' + self.version + '''

DFT is a collection of tools used to create Debian based firmwares

Available commands are :
. assemble_firmware                Create a firmware from a rootfs and generate the configuration files used to loading after booting
. build_image                      Build the disk image from the firmware (or rootfs) and bootchain
. build_firmware                   Build the firmware configuration files and scripts used to load in memory the firmware
. build_partitions                 Build the disk partitions and store them into separate files
. build_rootfs                     Generate a debootstrap from a Debian repository, install and configure required packages
. check_rootfs                     Control the content of the rootfs rootfs after its generation (debsecan and openscap)
? generate_content_information     Generate a manifest identiyfing content and versions
. install_bootchain                Install the bootchain (kernel, initramfs, grub or uboot) in the rootfs
. strip_rootfs                     Strip down the rootfs before assembling the firmware'''),
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
    """ This method build the parser, add all options and run it. The result of
    parser execution is stored in a member variable.
    """

    # Stores the argument in the instance
    self.command = args

    self.__add_parser_common()
# TODO command build project

    # According to the command, call the method dedicated to parse the arguments
    if self.command == Key.ASSEMBLE_FIRMWARE.value:
      self.__add_parser_assemble_firmware()
    elif self.command == Key.BUILD_ROOTFS.value:
      self.__add_parser_build_rootfs()
    elif self.command == Key.INSTALL_BOOTCHAIN.value:
      self.__add_parser_install_bootchain()
    elif self.command == Key.BUILD_IMAGE.value:
      self.__add_parser_build_image()
    elif self.command == Key.BUILD_PARTITIONS.value:
      self.__add_parser_build_partitions()
    elif self.command == Key.BUILD_FIRMWARE.value:
      self.__add_parser_build_firmware()
    elif self.command == Key.CHECK_ROOTFS.value:
      self.__add_parser_check_rootfs()
    elif self.command == Key.GEN_CONTENT_INFO.value:
      self.__add_parser_generate_content()
    elif self.command == Key.STRIP_ROOTFS.value:
      self.__add_parser_strip_rootfs()
    else:
      # If the command word is unknown, the force the parsing of the help flag
      return self.parser.parse_args(['-h'])

    # Finally call the parser that has been completed by the previous lines
    self.args = self.parser.parse_args()

  def __add_parser_assemble_firmware(self):
    """ This method add parser options specific to assemble_firmware command
    """

    # Add the arguments
    self.parser.add_argument(Key.ASSEMBLE_FIRMWARE.value,
                             help=Key.OPT_HELP_LABEL.value)


  def __add_parser_build_rootfs(self):
    """ This method add parser options specific to build_rootfs command
    """

    # Add the arguments
    self.parser.add_argument(Key.BUILD_ROOTFS.value,
                             help=Key.OPT_HELP_LABEL.value)

    # Overrides the target architecture from the configuration file by
    # limiting it to a given list of arch. Architectures not defined in
    # the configuration file can be added with this parameter
# TODO: parse the list of argument. So far only one value is handled
    self.parser.add_argument(Key.OPT_LIMIT_ARCH.value,
                             action='store',
                             dest=Key.LIMIT_TARGET_ARCH.value,
                             help="limit the list of target arch to process (comma separated list"
                                  " of arch eg: arch1,arch2)")

    # Overrides the target board used to build the rootfs. Board to
    # use is limited it to a given list of arch. Boards not defined
    # in the configuration file can be added with this parameter
# TODO: parse the list of argument. So far only one value is handled
    self.parser.add_argument(Key.OPT_LIMIT_BOARD.value,
                             action='store',
                             dest=Key.LIMIT_TARGET_BOARD.value,
                             help="limit the list of target board to process (comma separated "
                                  "list of versions eg: raspberry-pi-3, odroid-xu4)")

    # Overrides the target version used to build the rootfs. Version to
    # use is limited it to a given list of arch. Versions not defined
    # in the configuration file can be added with this parameter
# TODO: parse the list of argument. So far only one value is handled
    self.parser.add_argument(Key.OPT_LIMIT_VERSION.value,
                             action='store',
                             dest=Key.LIMIT_TARGET_VERSION.value,
                             help="limit the list of target version to process (comma separated "
                                  "list of versions eg: jessie,stretch)")

    # Override the list of mirrors defined in the configuration file.
    # This option defines a single mirror, not a full list of mirrors.
    # Thus the list of mirrors will be replaced by a single one
    self.parser.add_argument(Key.OPT_OVERRIDE_DEBIAN_MIRROR.value,
                             action='store',
                             dest=Key.OVERRIDE_DEBIAN_MIRROR.value,
                             help="override the list of mirrors defined in the configuration file."
                                  " This option\ndefines a single mirror, not a full list of "
                                  "mirrors. Thus the list of mirrors\nwill be replaced by a single"
                                  " one")

    # During installation ansible files from DFT toolkit are copied to
    # /dft_bootstrap in the target rootfs. This option prevents DFT from
    # removing these files. This is useful to debug ansible stuff and
    # replay an playbooks at will
    self.parser.add_argument(Key.OPT_KEEP_BOOTSTRAP_FILES.value,
                             action='store_true',
                             dest=Key.KEEP_BOOTSTRAP_FILES.value,
                             help="do not delete DFT bootstrap files after installation (debug "
                                  "purpose)")



  def __add_parser_install_bootchain(self):
    """ This method add parser options specific to install_bootchain command
    """

    # Add the arguments
    self.parser.add_argument(Key.INSTALL_BOOTCHAIN.value,
                             help=Key.OPT_HELP_LABEL.value)



  def __add_parser_build_image(self):
    """ This method add parser options specific to build_image command
    """


    # Add the arguments
    self.parser.add_argument(Key.BUILD_IMAGE.value,
                             help=Key.OPT_HELP_LABEL.value)



  def __add_parser_build_partitions(self):
    """ This method add parser options specific to build_partitions command
    """


    # Add the arguments
    self.parser.add_argument(Key.BUILD_PARTITIONS.value,
                             help=Key.OPT_HELP_LABEL.value)



  def __add_parser_build_firmware(self):
    """ This method add parser options specific to build_firmware command
    """

    # Add the arguments
    self.parser.add_argument(Key.BUILD_FIRMWARE.value,
                             help=Key.OPT_HELP_LABEL.value)



  def __add_parser_check_rootfs(self):
    """ This method add parser options specific to check_rootfs command
    """

    # Add the arguments
    self.parser.add_argument(Key.CHECK_ROOTFS.value,
                             help=Key.OPT_HELP_LABEL.value)



  def __add_parser_generate_content(self):
    """ This method add parser options specific to generate_content_information
    command
    """

    # Add the arguments
    self.parser.add_argument(Key.GEN_CONTENT_INFO.value,
                             help=Key.OPT_HELP_LABEL.value)

    # Activate the generation of the packages information.
    # Default behavior is to generate everything if no generate_xxx_information
    # flag is set. If at least one fag is set, then the user has to set every
    # needed flag
    self.parser.add_argument(Key.OPT_GEN_PACKAGES_INFO.value,
                             action='store_true',
                             dest=Key.GEN_PACKAGES_INFO.value,
                             help="generate the information about packages. If at least one of "
                                  "the\ngenerate_something_information is set,then it deactivate "
                                  "the 'generate all'\ndefault behavior, and each information "
                                  "source has to be set.\n")

    # Activate the generation of information about vulnerabilities
    self.parser.add_argument(Key.OPT_GEN_VULNERABILITIES_INFO.value,
                             action='store_true',
                             dest=Key.GEN_VULNERABILITIES_INFO.value,
                             help="generate the information about vulnerabilities.\n")

    # Activate the generation of information about security
    self.parser.add_argument(Key.OPT_GEN_SECURITY_INFO.value,
                             action='store_true',
                             dest=Key.GEN_SECURITY_INFO.value,
                             help="generate the information about security.\n")

    # Activate the generation of information about rootkit
    self.parser.add_argument(Key.OPT_GEN_ROOTKIT_INFO.value,
                             action='store_true',
                             dest=Key.GEN_ROOTKIT_INFO.value,
                             help="generate the information about rootkits.\n")

    # Activate the generation of information about files.
    self.parser.add_argument(Key.OPT_GEN_FILES_INFO.value,
                             action='store_true',
                             dest=Key.GEN_FILES_INFO.value,
                             help="generate the information about files.\n")

    # Activate the generation of information about the anti-virus execution.
    self.parser.add_argument(Key.OPT_GEN_ANTIVIRUS_INFO.value,
                             action='store_true',
                             dest=Key.GEN_ANTIVIRUS_INFO.value,
                             help="generate the information about anti-virus execution.\n")



  def __add_parser_strip_rootfs(self):
    """ This method add parser options specific to strip_rootfs command
    """

    # Add the arguments
    self.parser.add_argument(Key.STRIP_ROOTFS.value,
                             help=Key.OPT_HELP_LABEL.value)



  def __add_parser_common(self):
    """ This method add parser options common to all command
    Configuration file store the definition of rootfs. Option can be
    overriden by arguments on the command line (like --target-arch)
    """

    # Configuration file defines rootfs and its modulation
    self.parser.add_argument(Key.OPT_CONFIG_FILE.value,
                             action='store',
                             dest=Key.CONFIG_FILE.value,
                             default=Key.DEFAULT_CONFIGURATION_FILE.value,
                             help='DFT configuration file')

    # Project definition file defines environnement shared between
    # the different DFT commands (such as path to diirectory storing)
    # temporary working dir, temp dir name patterns, etc.)
    self.parser.add_argument(Key.OPT_PROJECT_FILE.value,
                             action='store',
                             dest=Key.PROJECT_FILE.value,
                             default=Key.DEFAULT_PROJECT_FILE.value,
                             required=True,
                             help='project definition file')

    # Defines the level of the log to output
    self.parser.add_argument(Key.OPT_LOG_LEVEL.value,
                             action='store',
                             dest=Key.LOG_LEVEL.value,
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
    if self.args.config_file is None:
      self.dft = model.DftConfiguration()
    else:
      self.dft = model.DftConfiguration(filename=self.args.config_file)
    self.dft.load_configuration()

    # Create the project definition object, and load its configuration
    self.project = model.ProjectDefinition(filename=self.args.project_file, configuration=self.dft)
    self.project.load_definition()

    # ---------------------------------------------------------------------
    # Override configuration with values passed on the commande line

    # Get the log_level from command line
    if self.args.log_level != None:
      self.project.dft.log_level = self.args.log_level.upper()
    # If not command line value, defaults to log
    else:
      self.project.dft.log_level = Key.LOG_LEVEL_INFO.value

    # Create the logger object
    logging.basicConfig()
    self.project.logging = logging.getLogger()
    self.project.logging.setLevel(self.project.dft.log_level)

    # Get the config file from command line
    if self.args.config_file != None and \
       self.args.config_file != self.project.dft.filename:
      self.project.logging.debug("Overriding config_file with CLI value : %s => %s",
                                 self.project.dft.filename,
                                 self.args.config_file)
      self.project.dft.filename = self.args.config_file

    # ---------------------------------------------------------------------

    # Select the method to run according to the command
    if self.command == Key.ASSEMBLE_FIRMWARE.value:
      self.__run_assemble_firmware()
    elif self.command == Key.BUILD_ROOTFS.value:
      self.__run_build_rootfs()
    elif self.command == Key.INSTALL_BOOTCHAIN.value:
      self.__run_install_bootchain()
    elif self.command == Key.BUILD_IMAGE.value:
      self.__run_build_image()
    elif self.command == Key.BUILD_FIRMWARE.value:
      self.__run_build_firmware()
    elif self.command == Key.BUILD_PARTITIONS.value:
      self.__run_build_partitions()
    elif self.command == Key.CHECK_ROOTFS.value:
      self.__run_check_rootfs()
    elif self.command == Key.GEN_CONTENT_INFO.value:
      self.__run_generate_content()
    elif self.command == Key.STRIP_ROOTFS.value:
      self.__run_strip_rootfs()



  # -------------------------------------------------------------------------
  #
  # __run_assemble_firmware
  #
  # -------------------------------------------------------------------------
  def __run_assemble_firmware(self):
    """ Method used to handle the assemble_firmware command.
    Create the business objet, then execute the entry point
    """

    # Create the business object
    command = assemble_firmware.AssembleFirmware(self.dft, self.project)

    # Then call the dedicated method
    command.assemble_firmware()



  # -------------------------------------------------------------------------
  #
  # __run_build_rootfs
  #
  # -------------------------------------------------------------------------
  def __run_build_rootfs(self):
    """ Method used to handle the build_rootfs command.
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
      if self.args.override_debian_mirror != self.project.project[Key.PROJECT_DEFINITION.value]\
                                                                 [Key.DEBOOTSTRAP_REPOSITORY.value]:
        self.project.logging.debug("Overriding pkg_archive_url with CLI value : %s => %s",
                                   self.project.project[Key.PROJECT_DEFINITION.value]\
                                                       [Key.DEBOOTSTRAP_REPOSITORY.value],
                                   self.args.override_debian_mirror)
        self.project.project[Key.PROJECT_DEFINITION.value][Key.DEBOOTSTRAP_REPOSITORY.value] = \
                                   self.args.override_debian_mirror

    if self.args.limit_target_version != None:
      if self.args.limit_target_version != self.project.get_target_version():
        self.project.logging.debug("Overriding target_version with CLI value : %s => %s",
                                   self.project.get_target_version(),
                                   self.args.limit_target_version)
        self.project.set_version(self.args.limit_target_version)

    if self.args.limit_target_board != None:
      if self.args.limit_target_board != self.project.get_target_board():
        self.project.logging.debug("Overriding target_board with CLI value : %s => %s",
                                   self.project.get_target_board(),
                                   self.args.limit_target_board)
        self.project.set_board(self.args.limit_target_board)

    if self.args.limit_target_arch != None:
      if self.args.limit_target_arch != self.project.get_target_arch():
        self.project.logging.debug("Overriding target_arch with CLI value : %s => %s",
                                   self.project.get_target_arch(),
                                   self.args.limit_target_arch)
        self.project.set_arch(self.args.limit_target_arch)

    # Create the business object
    command = build_rootfs.BuildRootFS(self.dft, self.project)

    # Then call the dedicated method
    command.create_rootfs()



  # -------------------------------------------------------------------------
  #
  # __run_install_bootchain
  #
  # -------------------------------------------------------------------------
  def __run_install_bootchain(self):
    """ Method used to handle the install_bootchain command.
    Create the business objet, then execute the entry point.
    """

    # Create the business object
    command = install_bootchain.InstallBootChain(self.dft, self.project)

    # Then call the dedicated method
    command.install_bootchain()



  # -------------------------------------------------------------------------
  #
  # __run_build_image
  #
  # -------------------------------------------------------------------------
  def __run_build_image(self):
    """ Method used to handle the build_image command.
    Create the business objet, then execute the entry point.
    """

    # Create the business object
    command = build_image.BuildImage(self.dft, self.project)

    # Then call the dedicated method
    command.build_image()



  # -------------------------------------------------------------------------
  #
  # __run_build_partitions
  #
  # -------------------------------------------------------------------------
  def __run_build_partitions(self):
    """ Method used to handle the build_partition command.
    Create the business objet, then execute the entry point.

    Partition building is handled by the same business object as image building.
    Most of the code is common to both command.
    """

    # Create the business object
    command = build_image.BuildImage(self.dft, self.project)

    # Then call the dedicated method
    command.build_partitions()



  # -------------------------------------------------------------------------
  #
  # __run_build_firmware
  #
  # -------------------------------------------------------------------------
  def __run_build_firmware(self):
    """ Method used to handle the build_firmware command.
    Create the business objet, then execute the entry point.
    """

    # Create the business object
    command = build_firmware.BuildFirmware(self.dft, self.project)

    # Then call the dedicated method
    command.build_firmware()



  # -------------------------------------------------------------------------
  #
  # __run_check_rootfs
  #
  # -------------------------------------------------------------------------
  def __run_check_rootfs(self):
    """ Method used to handle the check_rootfs command.
    Create the business objet, then execute the entry point
    """

    # Create the business object
    command = check_rootfs.CheckRootFS(self.dft, self.project)

    # Then call the dedicated method
    command.check_rootfs()



  # -------------------------------------------------------------------------
  #
  # __run_generate_content
  #
  # -------------------------------------------------------------------------
  def __run_generate_content(self):
    """ Method used to handle the generate_content_information command.
    Create the business objet, then execute the entry point
    """

    # Check if we have to do a 'generate all' or if some more specific flags
    # have ben set to reduce output. Default is generate all to true and all
    # other flags to false
    self.project.dft.generate_all_information = True
    self.project.dft.gen_packages_info = False
    self.project.dft.gen_files_info = False
    self.project.dft.gen_antivirus_info = False
    self.project.dft.gen_vulnerabilities_info = False
    self.project.dft.gen_security_info = False

    # Check if the packages are needed
    if self.args.gen_packages_info != None:
      # Flag is defined, then copy it
      self.project.dft.gen_packages_info = self.args.gen_packages_info
      # If flag is true, then generate all as to be false
      if self.project.dft.gen_packages_info:
        self.project.dft.generate_all_information = False

    # Check if the files are needed
    if self.args.gen_files_info != None:
      # Flag is defined, then copy it
      self.project.dft.gen_files_info = self.args.gen_files_info
      # If flag is true, then generate all as to be false
      if self.project.dft.gen_files_info:
        self.project.dft.generate_all_information = False

    # Check if the vulnerabilties are needed
    if self.args.gen_vulnerabilities_info != None:
      # Flag is defined, then copy it
      self.project.dft.gen_vulnerabilities_info = self.args.gen_vulnerabilities_info
      # If flag is true, then generate all as to be false
      if self.project.dft.gen_vulnerabilities_info:
        self.project.dft.generate_all_information = False

    # Check if the antivirus are needed
    if self.args.gen_antivirus_info != None:
      # Flag is defined, then copy it
      self.project.dft.gen_antivirus_info = self.args.gen_antivirus_info
      # If flag is true, then generate all as to be false
      if self.project.dft.gen_antivirus_info:
        self.project.dft.generate_all_information = False

    # Check if the security are needed
    if self.args.gen_security_info != None:
      # Flag is defined, then copy it
      self.project.dft.gen_security_info = self.args.gen_security_info
      # If flag is true, then generate all as to be false
      if self.project.dft.gen_security_info:
        self.project.dft.generate_all_information = False

    # Check if the rootkit are needed
    if self.args.gen_rootkit_info != None:
      # Flag is defined, then copy it
      self.project.dft.gen_rootkit_info = self.args.gen_rootkit_info
      # If flag is true, then generate all as to be false
      if self.project.dft.gen_rootkit_info:
        self.project.dft.generate_all_information = False

    # Create the business object
    command = generate_content_information.GenerateContentInformation(self.dft, self.project)

    # Then call the dedicated method
    command.gen_content_info()


  # -------------------------------------------------------------------------
  #
  # __run_strip_rootfs
  #
  # -------------------------------------------------------------------------
  def __run_strip_rootfs(self):
    """ Method used to handle the strip_rootfs command.
      Create the business objet, then execute the entry point
    """

    # Create the business object
    command = strip_rootfs.StripRootFS(self.dft, self.project)

    # Then call the dedicated method
    command.strip_rootfs()


# TODO add clean-dir option to build and assemble firmware. What is the strategy for cleaning and
# recycling previous content
# maybe more working dir, and a final output ?
