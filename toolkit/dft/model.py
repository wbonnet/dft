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


""" This module contains the definition of the two main classes used in DFT model.
The Project and the Configuration. The classes implements the methods used to load
their content and definition fom yaml configuration file.
"""

import os
import subprocess
import logging
from datetime import datetime
import yaml
from dft.enumkey import Key

# -----------------------------------------------------------------------------
#
# class Configuration
#
# -----------------------------------------------------------------------------
class Configuration(object):
  """This class defines default configuration for the DFT toolchain

  The tool configuration contains environment variables used to define
  information such as default root working path, etc.

  The values stored in this object are read from the following sources,
  in order of priority (from the highest priority to the lowest).
  """

  # ---------------------------------------------------------------------------
  #
  # __init__
  #
  # ---------------------------------------------------------------------------
  def __init__(self, filename=None):
    """
    """

    # Default configuration file to use if none is provided through the cli
    if filename is None:
      self.filename = "~/.dftrc"
    else:
      self.filename = filename

    # Debootstrap target to use (minbase or buildd)
    self.debootstrap_target = "minbase"

    # Path to the default directory ued to store rootfs
    # It defaults to /tmp
    self.working_directory = None

    # During installation ansible files from DFT toolkit are copied to
    # /dft_bootstrap in the target rootfs. This falgs prevents DFT from
    # removing these files if set to True. This is useful to debug
    # ansible stuff and replay an playbooks at will
    self.keep_bootstrap_files = False

    # Initialize members used in configuration
    self.project_name = None
    self.logging = logging.getLogger()
    self.configuration = None

    #
    # Information generation flags. Each of the following flag controls the generation
    # of a given section.
    #
    self.list_all_content = None
    self.content_packages = None
    self.content_vulnerabilities = None
    self.content_rootkit = None
    self.content_security = None
    self.content_files = None
    self.content_antivirus = None

    # Name of the sequence to run
    self.sequence_name = None

  # ---------------------------------------------------------------------------
  #
  # load_configuration
  #
  # ---------------------------------------------------------------------------
  def load_configuration(self, filename=None):
    """ This method load the tool configuration from the given YAML file
    """

    # If a new filename has been passed as argument, then store it
    if filename is not None:
      self.filename = filename

    # Expend ~ as uer home dir
    self.filename = os.path.expanduser(self.filename)

    # Check if configuration file exist in home ir, otherwise switch to package config file
    if not os.path.isfile(self.filename):
      self.filename = "/etc/dft/dftrc"

    # No then it does not matter, let('s continue without ~/.dftrc file
    self.logging.debug("Using configuration file : " + self.filename)

    try:
      # Check it the configuration file exist
      if os.path.isfile(self.filename):
        # Yes then, load it
        with open(self.filename, 'r') as working_file:
          self.configuration = yaml.load(working_file)

          # Now we may have to expand a few paths...
          # First check if the configurationis really defined
          if self.configuration is not None and Key.CONFIGURATION.value in self.configuration:
            # Yes then we now have to check one by one th different path to expand
            # First let's process working_dir
            if Key.WORKING_DIR.value in self.configuration[Key.CONFIGURATION.value]:
              self.configuration[Key.CONFIGURATION.value][Key.WORKING_DIR.value] = \
                        os.path.expanduser(self.configuration[Key.CONFIGURATION.value]\
                                                             [Key.WORKING_DIR.value])
            # Then let's do dft_base
            if Key.DFT_BASE.value in self.configuration[Key.CONFIGURATION.value]:
              self.configuration[Key.CONFIGURATION.value][Key.DFT_BASE.value] = \
                        os.path.expanduser(self.configuration[Key.CONFIGURATION.value]\
                                                             [Key.DFT_BASE.value])
            # And finally the list of additionnal roles
            if Key.ADDITIONAL_ROLES.value in self.configuration[Key.CONFIGURATION.value]:
              # Check if path starts with ~ and need expension
              for i in range(0, len(self.configuration[Key.CONFIGURATION.value]\
                                                      [Key.ADDITIONAL_ROLES.value])):
                self.configuration[Key.CONFIGURATION.value][Key.ADDITIONAL_ROLES.value][i] = \
                   os.path.expanduser(self.configuration[Key.CONFIGURATION.value]\
                                                        [Key.ADDITIONAL_ROLES.value][i])
      else:
        # No then it does not matter, let('s continue without ~/.dftrc file
        self.logging.debug("The file " + self.filename + " does not exist. Aborting.")

    except OSError as exception:
      # Call clean up to umount /proc and /dev
      self.logging.critical("Error: " + exception.filename + "- " + exception.strerror)
      exit(1)

# -----------------------------------------------------------------------------
#
# Class Project
#
# -----------------------------------------------------------------------------
class Project(object):
  """This class defines a project. A project holds all the information used
  to produce the different object created by DFT (rootfs, modulations,
  firmware, bootlader, etc.).

  Project is an aggregation of several dedicated configuration and
  definition object. It also includes tool configuration by itself.
  """

  # ---------------------------------------------------------------------------
  #
  # __init__
  #
  # ---------------------------------------------------------------------------
  def __init__(self, configuration, filename=None):
    """
    """

    # Stores the configuration used for this project
    self.dft = configuration

    # Create the logger object
    self.logging = logging.getLogger()

    # Store the filename containing the whole project definition
    # Filename is mandatory, and is defaulted to project.yml if
    # not defined
    if filename is None:
      self.project_name = Key.PROJECT_NAME.value
    else:
      self.project_name = filename

    # Timestamp is used to produce distinct directory in case of several
    # run, and also used to produce the serial number (/etc/dft_version)
    self.timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    # Defines path for subcommand
    self.rootfs_base_workdir = None
    self.image_base_workdir = None
    self.bootchain_base_workdir = None
    self.firmware_base_workdir = None
    self.content_base_workdir = None

    # Defines member variables
    self.archive_filename = None
    self.firmware_filename = None
    self.init_filename = None

    self.targets = None
    self.rootfs = None
    self.check = None
    self.content_information = None
    self.firmware = None
    self.image = None
    self.project_base_workdir = None
    self.project = None
    self.repositories = None
    self.stripping = None
    self.variables = None



  # ---------------------------------------------------------------------------
  #
  # get_target_arch
  #
  # ---------------------------------------------------------------------------
  def get_target_arch(self, index=0):
    """ Simple getter to access the arch of n-th item in the targets to produce
    list. It is designed to reduce caller code complexity, and hide internal
    data structure.

    If no index is provided it returns the first element, or None if the
    array is empty.
    """

    # Check if the array is empty
    if len(self.project[Key.PROJECT_DEFINITION.value][Key.TARGETS.value]) == 0:
      # Yes thus, returns None
      return None
    # Otherwise returns the n-th item
    else:
      return self.project[Key.PROJECT_DEFINITION.value][Key.TARGETS.value][index]\
                         [Key.BSP.value][Key.ARCHITECTURE.value]



  # ---------------------------------------------------------------------------
  #
  # get_target_board
  #
  # ---------------------------------------------------------------------------
  def get_target_board(self, index=0):
    """ Simple getter to access the board of n-th item in the targets to produce
    list. It is designed to reduce caller code complexity, and hide internal
    data structure.

    If no index is provided it returns the first element, or None if the
    array is empty.
    """

    # Check if the array is empty
    if len(self.project[Key.PROJECT_DEFINITION.value][Key.TARGETS.value]) == 0:
      # Yes thus, returns None
      return None
    # Otherwise returns the n-th item
    else:
      return self.project[Key.PROJECT_DEFINITION.value][Key.TARGETS.value][index]\
                         [Key.BOARD.value]



  # ---------------------------------------------------------------------------
  #
  # get_target_version
  #
  # ---------------------------------------------------------------------------
  def get_target_version(self, index=0):
    """ Simple getter to access the version of n-th item in the targets to produce
    list. It is designed to reduce caller code complexity, and hide internal
    data structure.

    If no index is provided it returns the first element, or None if the
    array is empty.
    """

    # Check if the array is empty
    # if len(self.project[Key.PROJECT_DEFINITION.value][Key.TARGETS.value]) == 0:
    #   # Yes thus, returns None
    #   return None
    # # Otherwise returns the n-th item
    # else:
    return self.project[Key.PROJECT_DEFINITION.value][Key.TARGETS.value][index]\
                         [Key.VERSION.value]



  # ---------------------------------------------------------------------------
  #
  # generate_def_file_path
  #
  #   This method generates the complete path to sub configuration files
  #   This files are referenced in the project configuration file, and are
  #   supposed to be in the same folder as the project file
  #
  #   A "project-path' can be defined in the project file. If defined, the
  #   files are loaded from this place. If not, they are loaded from the
  #   directory containing the project file being used.
  #
  # ---------------------------------------------------------------------------
  def generate_def_file_path(self, filename):
    """ This method generate the path to a configuration file. Generated path is
    relative to project-path if this variable has been set in the ain project file.
    If the variable has not been set, configuration files are searched in the same
    directory as project.yml (main project file).
    """

    # Check if the project path is defined into the project file
    if Key.CONFIGURATION.value in self.project and \
       self.project[Key.CONFIGURATION.value] is not None:
      if Key.PROJECT_PATH.value in self.project[Key.CONFIGURATION.value]:
        filename = self.project[Key.CONFIGURATION.value][Key.PROJECT_PATH.value] + "/" + filename
    else:
      filename = "./" + filename

    # Return what has been generated
    return filename



  # ---------------------------------------------------------------------------
  #
  # load_definition
  #
  # ---------------------------------------------------------------------------
  def load_definition(self, filename=None):
    """ This method loads the project file, parse it and then loads each definition
    file it includes. Each definition file is a yaml file which is loaded directly
    to a dictionnary in memory.
    """

    # Test if the filename has been redefinied
    if filename != None:
      self.project_name = filename
      self.logging.debug("setting new project filename : " + self.project_name)

    # Need some debug output :)
    self.logging.debug("loading project : " + self.project_name)

    # Enter a try except section. This is how we handle missing files, through
    # exception mecanism. If a FileNotFoundError is raised, then exit the
    # program
    try:
      #
      # Load all the sub configuration files from disk
      #
      with open(self.project_name, 'r') as working_file:
        self.project = yaml.load(working_file)

        # Check if there is a configuration and working file defined, otherwise copy
        # it from the general configuration
        if Key.CONFIGURATION.value not in self.project or \
           self.project[Key.CONFIGURATION.value] is None:
          # Not, thus is global configuration is defined, let's copy it
          if Key.BSP_BASE.value in self.dft.configuration[Key.CONFIGURATION.value]:
            self.project[Key.CONFIGURATION.value] = self.dft.configuration[Key.CONFIGURATION.value]
          else:
            # Create the empty configuration if not defined
            self.project[Key.CONFIGURATION.value] = {}

        # We try to expand variables only if some keys have been defined under configuration
        if Key.CONFIGURATION.value in self.project and \
           self.project[Key.CONFIGURATION.value] is not None:
          # Expand ~ in path since it is not done automagically by Python
          for key in {Key.DFT_BASE.value, Key.PROJECT_PATH.value, Key.WORKING_DIR.value}:
            # For iterate the key and check they are defined in the config file
            if key in self.project[Key.CONFIGURATION.value] and \
               self.project[Key.CONFIGURATION.value][key] is not None:
              # If yes modifiy its value using expenduser ( replace ~ by /home/foo)
              self.project[Key.CONFIGURATION.value][key] = \
                              os.path.expanduser(self.project[Key.CONFIGURATION.value][key])
            else:
              if key in self.dft.configuration[Key.CONFIGURATION.value]:
                self.project[Key.CONFIGURATION.value][key] = \
                                      self.dft.configuration[Key.CONFIGURATION.value][key]
              else:
                # If key is not found, we have to setup some default values
                # If project_path is not defined, then we use the directory containing the project
                # file we have loaded
                # Use /tmp/working_dir for working dir and /usr/share/dft for dft base
                if key == Key.PROJECT_PATH.value:
                  self.project[Key.CONFIGURATION.value][key] = os.path.dirname(self.project_name)
                  # Check if the path is empty. This happens when dft is run from the directory
                  # containing the project file itself. In such cases path will be empty, and
                  # we have top doify it , otherwise absolute path might be generated by
                  # concatenation. It defaults to "./""
                  if self.project[Key.CONFIGURATION.value][key] == "":
                    self.project[Key.CONFIGURATION.value][key] = "./"
                elif key == Key.WORKING_DIR.value:
                  self.project[Key.CONFIGURATION.value][key] = "/tmp/working_dir"
                elif key == Key.DFT_BASE.value:
                  self.project[Key.CONFIGURATION.value][key] = "/usr/share/dft"

          # Expand ~ in path since it is not done automagically by Python
          for key in {Key.ADDITIONAL_ROLES.value}:
            # For iterate the key and check they are defined in the config file
            if key in self.project[Key.CONFIGURATION.value] and \
           self.project[Key.CONFIGURATION.value] is not None:
              # Then iterate the list of values it contains
              for counter in range(len(self.project[Key.CONFIGURATION.value][key])):
                self.project[Key.CONFIGURATION.value][key][counter] = \
                      os.path.expanduser(self.project[Key.CONFIGURATION.value][key][counter])

      # Load the repositories sub configuration files
      if Key.REPOSITORIES.value in self.project[Key.PROJECT_DEFINITION.value]:
        filename = self.generate_def_file_path(self.project[Key.PROJECT_DEFINITION.value]\
                                                           [Key.REPOSITORIES.value][0])
        with open(filename, 'r') as working_file:
          self.repositories = yaml.load(working_file)

      # Load the rootfs sub configuration files
      if Key.ROOTFS.value in self.project[Key.PROJECT_DEFINITION.value]:
        filename = self.generate_def_file_path(self.project[Key.PROJECT_DEFINITION.value]\
                                                           [Key.ROOTFS.value][0])
        with open(filename, 'r') as working_file:
          self.rootfs = yaml.load(working_file)

      # Load the firmware sub configuration files
      if Key.FIRMWARE.value in self.project[Key.PROJECT_DEFINITION.value]:
        filename = self.generate_def_file_path(self.project[Key.PROJECT_DEFINITION.value]\
                                                           [Key.FIRMWARE.value][0])
        with open(filename, 'r') as working_file:
          self.firmware = yaml.load(working_file)

      # Load the image sub configuration files
      if Key.IMAGE.value in self.project[Key.PROJECT_DEFINITION.value]:
        filename = self.generate_def_file_path(self.project[Key.PROJECT_DEFINITION.value]\
                                                           [Key.IMAGE.value][0])
        with open(filename, 'r') as working_file:
          self.image = yaml.load(working_file)

      # Load the check sub configuration files
      if Key.CHECK.value in self.project[Key.PROJECT_DEFINITION.value]:

        # Initialize the rule dictionnary
        self.check = []

        # Iterate the list of stripping rule files
        if self.project[Key.PROJECT_DEFINITION.value][Key.CHECK.value] is not None:
          for check_file in self.project[Key.PROJECT_DEFINITION.value][Key.CHECK.value]:
            # Get th full path of the file to load
            filename = self.generate_def_file_path(check_file)

            # Open and read the file
            with open(filename, 'r') as working_file:
              # YAML structure is stored at index 'counter'
              self.check.append(yaml.load(working_file))

      # Load the stripping sub configuration files
      if Key.STRIPPING.value in self.project[Key.PROJECT_DEFINITION.value]:

        # Initialize the rule dictionnary
        self.stripping = []

        # Iterate the list of stripping rule files
        if self.project[Key.PROJECT_DEFINITION.value][Key.STRIPPING.value] is not None:
          for stripping_file in self.project[Key.PROJECT_DEFINITION.value][Key.STRIPPING.value]:
            # Get th full path of the file to load
            filename = self.generate_def_file_path(stripping_file)

            # Open and read the file
            with open(filename, 'r') as working_file:
              # YAML structure is stored at index 'counter'
              self.stripping.append(yaml.load(working_file))


      # Load the check sub configuration files
      if Key.CONTENT_INFORMATION.value in self.project[Key.PROJECT_DEFINITION.value]:
        filename = self.generate_def_file_path(self.project[Key.PROJECT_DEFINITION.value]\
                                                               [Key.CONTENT_INFORMATION.value][0])
        with open(filename, 'r') as working_file:
          self.content_information = yaml.load(working_file)

      # Load the list of variables files
      if Key.VARIABLES.value in self.project[Key.PROJECT_DEFINITION.value]:
        filename = self.generate_def_file_path(self.project[Key.PROJECT_DEFINITION.value]\
                                                               [Key.VARIABLES.value][0])
        with open(filename, 'r') as working_file:
          self.variables = yaml.load(working_file)

      #
      # Once configuration have been loaded, compute the values of some
      # configuration variables
      #

      # First use value from configuration, then override it with value from project if defined.
      # Writing it this way simplifies the if then else processing.
      self.logging.debug(self.dft.configuration)
      if Key.WORKING_DIR.value in self.dft.configuration[Key.CONFIGURATION.value]:
        self.project_base_workdir = self.dft.configuration[Key.CONFIGURATION.value]\
                                                                    [Key.WORKING_DIR.value]
        self.logging.debug("Using working_dir from configuration : " + self.project_base_workdir)
      else:
        self.logging.debug("configuration/working_dir is not defined, using /tmp/dft as default")
        self.project_base_workdir = "/tmp/dft"

      # Now check if a value from prject is defined and should override current value
      if Key.CONFIGURATION.value in self.project:
        if Key.WORKING_DIR.value in self.project[Key.CONFIGURATION.value]:
          self.project_base_workdir = self.project[Key.CONFIGURATION.value][Key.WORKING_DIR.value]
          self.logging.debug("Using working_dir from project : " + self.project_base_workdir)

      self.project_base_workdir += "/" + self.project[Key.PROJECT_DEFINITION.value]\
                                                     [Key.PROJECT_NAME.value]

      # Defines path for subcommand
      self.rootfs_base_workdir = self.project_base_workdir + "/rootfs"
      self.image_base_workdir = self.project_base_workdir + "/image"
      self.bootchain_base_workdir = self.project_base_workdir + "/bootchain"
      self.firmware_base_workdir = self.project_base_workdir + "/firmware"
      self.content_base_workdir = self.project_base_workdir + "/content"

      # Retrieve the target components (version and board)
      if Key.TARGETS.value in self.project[Key.PROJECT_DEFINITION.value]:
        # Iterate the list of targets in order to load th BSP definition file
        for target in self.project[Key.PROJECT_DEFINITION.value][Key.TARGETS.value]:
          # Test if a specific BSP file is provided
          if Key.BSP_FILE.value in target:
            bsp_file = target[Key.BSP_FILE.value]
          else:
            # Check if the __native__ arch is defined. If yesm qrch is change to
            # generic-what_we_run_on'
            if target[Key.BOARD.value].lower() == Key.NATIVE.value.lower():
              target[Key.BOARD.value] = "generic-" + self.get_native_arch()

            # There is specific file, thus use the default path
            # Build the path to the file containing the BSP definition
            bsp_file = self.get_bsp_base() + "/boards/" + target[Key.BOARD.value] + ".yml"

#FIXME: Does not choose configuration in right order. .dftrc BSP defined path not taken in account

          # Check that the BSP file exist
          if not os.path.isfile(bsp_file):
            self.logging.critical("The BSP file %s does not exist !", bsp_file)
            self.logging.critical("Cannot continue execution, please fix target in project file.")
            exit(1)
          else:
            self.logging.debug("loading BSP file " + bsp_file)
            with open(bsp_file, 'r') as working_file:
              target[Key.BSP.value] = yaml.load(working_file)

      # Defines the full path and filename to the firmware
      self.firmware_filename = self.get_firmware_content_directory() + "/"
      if self.firmware and Key.FILENAME.value in self.firmware[Key.SQUASHFS_CONFIGURATION.value] \
                       and len(self.firmware[Key.SQUASHFS_CONFIGURATION.value] \
                                            [Key.FILENAME.value]) > 0:
        self.firmware_filename += self.firmware[Key.SQUASHFS_CONFIGURATION.value]\
                                               [Key.FILENAME.value]
      else:
        self.firmware_filename += self.project[Key.PROJECT_DEFINITION.value][Key.PROJECT_NAME.value]
        self.firmware_filename += ".squashfs"

      # Defines the full path and filename to the init used by firmware
      self.init_filename = self.get_firmware_content_directory() + "/init"

    # Handle exception that may occur when trying to open unknown files
    except OSError as exception:
      # Just log and exit, nothing is mounted yet
      self.logging.critical("Error: %s - %s.", exception.filename, exception.strerror)
      exit(1)



  # ---------------------------------------------------------------------------
  #
  # __get_target_directory
  #
  # ---------------------------------------------------------------------------
  def __get_target_directory(self, index=0):
    """ This method compute and return the target component name used in the
    working directory generation (firmware_directory or rootfs_mountpoint as
    example). It is based upon values of current target (arch, board name and
    version).
    """

    # Compute the value of the firmware_directory
    target_directory = self.get_target_board(index) + "-" + self.get_target_arch(index) + "-"
    target_directory += self.get_target_version(index)

    # That's all folks :)
    return target_directory



  # ---------------------------------------------------------------------------
  #
  # get_firmware_content_directory
  #
  # ---------------------------------------------------------------------------
  def get_firmware_content_directory(self):
    """ This method compute and return the directory where the element
    composing are stored before final assembly. It is a subdirectory of the
    firmware directory itself, named components.
    """

    # Compute the value of the firmware_directory
    return self.firmware_base_workdir + "/" + self.__get_target_directory(0) + "/content"



  # ---------------------------------------------------------------------------
  #
  # get_firmware_output_directory
  #
  # ---------------------------------------------------------------------------
  def get_firmware_output_directory(self):
    """ This method compute and return the directory where the final fiware
    file and signature are stored.
    """

    # Compute the value of the firmware_directory
    return self.firmware_base_workdir + "/" + self.__get_target_directory(0)



  # ---------------------------------------------------------------------------
  #
  # get_rootfs_mountpoint
  #
  # ---------------------------------------------------------------------------
  def get_rootfs_mountpoint(self):
    """ This method compute and return the rootfs_mountpoint value based using
    the value of current target (arch, board name and version).
    """

    # Compute the value of the rootfs_mountpoint and return it to the caller
    return self.rootfs_base_workdir + "/" +  self.__get_target_directory(0)


  # ---------------------------------------------------------------------------
  #
  # get_image_directory
  #
  # ---------------------------------------------------------------------------
  def get_image_directory(self):
    """ This method compute and return the directory path for stoing images.
    """

    # Compute the value of the rootfs_mountpoint and return it to the caller
    return self.image_base_workdir + "/" +  self.__get_target_directory(0)

  # ---------------------------------------------------------------------------
  #
  # get_dft_base
  #
  # ---------------------------------------------------------------------------
  def get_dft_base(self):
    """ This method compute and return the dft_base based using the value of
    the project, or is not define from the configuration file, or from the
    default values.
    """

    # Project configuration exist. Is there a DFT base defined ?
    if Key.DFT_BASE.value not in self.project[Key.CONFIGURATION.value]:
      # No, then let's copy the key from global configuration, or use its default value
      if Key.DFT_BASE.value in self.project[Key.CONFIGURATION.value]:
        self.project[Key.CONFIGURATION.value][Key.DFT_BASE.value] = \
                      self.project[Key.CONFIGURATION.value][Key.DFT_BASE.value]
      else:
        # Global is not defined, then default to /usr/share value
        self.project[Key.CONFIGURATION.value][Key.DFT_BASE.value] = "/usr/share/dft"

    # Expand the path starting with ~/
    self.project[Key.CONFIGURATION.value][Key.DFT_BASE.value] = \
                      os.path.expanduser(self.project[Key.CONFIGURATION.value][Key.DFT_BASE.value])

    # Now a value is defined, just return it
    return self.project[Key.CONFIGURATION.value][Key.DFT_BASE.value]



  # ---------------------------------------------------------------------------
  #
  # get_bsp_base
  #
  # ---------------------------------------------------------------------------
  def get_bsp_base(self):
    """ This method compute and return the bsp_base directory using either the
    value defined in the project file, the configuration file, or from the
    default values.
    """

    # Project configuration exist. Is there a DFT base defined ?
    if Key.BSP_BASE.value not in self.project[Key.CONFIGURATION.value]:
      # No, then let's copy the key from global configuration, or use its default value
      if Key.BSP_BASE.value in self.dft.configuration[Key.CONFIGURATION.value]:
        self.project[Key.CONFIGURATION.value][Key.BSP_BASE.value] = \
                      self.dft.configuration[Key.CONFIGURATION.value][Key.BSP_BASE.value]
      else:
        # Global is not defined, then default to /usr/share/bsp value
        self.project[Key.CONFIGURATION.value][Key.BSP_BASE.value] = self.get_dft_base() + "/bsp"

    # Expand the path starting with ~/
    self.project[Key.CONFIGURATION.value][Key.BSP_BASE.value] = \
                      os.path.expanduser(self.project[Key.CONFIGURATION.value][Key.BSP_BASE.value])

    # Now a value is defined, just return it
    return self.project[Key.CONFIGURATION.value][Key.BSP_BASE.value]



  # -------------------------------------------------------------------------
  #
  # get_native_arch
  #
  # -------------------------------------------------------------------------
  def get_native_arch(self):
    """This method returns the native architecture of the host running DFT.
    Arch format is the same as dpkg tools if means arm64 instead of aarch64
    """

    # Retrieve the architecture of the host
    host_arch = subprocess.check_output("uname -m", shell=True).decode(Key.UTF8.value).rstrip()
    if host_arch == "x86_64":
      return "amd64"
    elif host_arch == "armv7l":
      return "armhf"
    elif host_arch == "aarch64":
      return "arm64"
    else:
      return host_arch

  # -------------------------------------------------------------------------
  #
  # get_mkimage_arch
  #
  # -------------------------------------------------------------------------
  def get_mkimage_arch(self):
    """This method returns the native architecture of the host running DFT.
    Arch format is the same as dpkg tools if means arm64 instead of aarch64
    """

    # Retrieve the architecture of the host
    arch = subprocess.check_output("uname -m", shell=True).decode(Key.UTF8.value).rstrip()
    if arch == "ppc64" or arch == "ppc64el" or arch == "ppc":
      return "powerpc"
    elif arch == "armv7l" or arch == "aarch64":
      return "arm"

    # Return arch in any case
    return arch

  # -------------------------------------------------------------------------
  #
  # get_image_content_mode
  #
  # -------------------------------------------------------------------------
  def get_image_content_mode(self):
    """This method returns the image content mode, which values are :
    . rootfs
    . firmware
    . unknown
    """

    # Retrieve the mode
    if self.project.image[Key.CONTENT.value][Key.TYPE.value].lower() == Key.ROOTFS.value:
      return Key.ROOTFS.value
    elif self.project.image[Key.CONTENT.value][Key.TYPE.value].lower() == Key.FIRMWARE.value:
      return Key.FIRMWARE.value

    # Still here ? thus type is unknown
    logging.critical("Unknown image content : " + self.project.image[Key.CONTENT.value]\
                       [Key.TYPE.value] + ". Aborting.")
    exit(1)

  # -------------------------------------------------------------------------
  #
  # is_image_content_rootfs
  #
  # -------------------------------------------------------------------------
  def is_image_content_rootfs(self):
    """This method returns TRUE if the image content mode is rootfs
    """

    # Check mode validity
    if not self.project.image[Key.CONTENT.value][Key.TYPE.value].lower() == Key.ROOTFS.value or \
       not self.project.image[Key.CONTENT.value][Key.TYPE.value].lower() == Key.FIRMWARE.value:
      logging.critical("Unknown image content : " + self.project.image[Key.CONTENT.value]\
                       [Key.TYPE.value] + ". Aborting.")
      exit(1)

    # Retrieve the mode
    if self.project.image[Key.CONTENT.value][Key.TYPE.value].lower() == Key.ROOTFS.value:
      return True
    else:
      return False


  # -------------------------------------------------------------------------
  #
  # is_image_content_firmware
  #
  # -------------------------------------------------------------------------
  def is_image_content_firmware(self):
    """This method returns TRUE if the image content mode is firmware
    """

    # Check mode validity
    if not self.image[Key.CONTENT.value][Key.TYPE.value].lower() == Key.ROOTFS.value or \
       not self.image[Key.CONTENT.value][Key.TYPE.value].lower() == Key.FIRMWARE.value:
      logging.critical("Unknown image content : " + self.image[Key.CONTENT.value][Key.TYPE.value] +\
                       ". Aborting.")
      exit(1)

    # Retrieve the mode
    if self.image[Key.CONTENT.value][Key.TYPE.value].lower() == Key.ROOTFS.value:
      return False
    else:
      return True
