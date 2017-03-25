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

import logging
import os
from datetime import datetime
import yaml


# TODO: add a method to initialize all defaut value and not do it into the code
# TODO : add enum with key strings ?

# -----------------------------------------------------------------------------
#
# class DftConfiguration
#
# -----------------------------------------------------------------------------
class DftConfiguration(object):
  """This class defines default configuration for the DFT toolchain

  The tool configuration contains environment variables used to define
  information such as default root working path, cache directories, etc.

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
      self.configuration_file = "~/.dftrc"
    else:
      self.configuration_file = filename

    # Boolean used to flag if the cache archive should used instead
    # of doing a real debootstrap installation
    self.use_cache_archive = False

    # Boolean used to flag if the cache archive should used updated
    # after doing a real debootstrap installation
    self.update_cache_archive = False

    # Debootstrap target to use (minbase or buildd)
    self.debootstrap_target = "minbase"

    # Path to the default directory ued to store rootfs and cache archives
    # It defaults to /tmp
# TODO : This may lead to full file system, should be changed, may be
# a mandatory value in the config file ? => change to None
    self.working_directory = None

    # During installation ansible files from DFT toolkit are copied to
    # /dft_bootstrap in the target rootfs. This falgs prevents DFT from
    # removing these files if set to True. This is useful to debug
    # ansible stuff and replay an playbooks at will
    self.keep_bootstrap_files = False

    # Initialize members used in configuration
    self.project_name = None
    self.logging = None
    self.dft_configuration = None


  # ---------------------------------------------------------------------------
  #
  # load_configuration
  #
  # ---------------------------------------------------------------------------
  def load_configuration(self, filename=None):
    """ This method load the tool configuration from the given YAML file
    """

# TODO handle filename
    try:
      # Load it
      with open(self.project_name, 'r') as working_file:
        self.logging.debug("loading dft configuration : " + filename)
        self.dft_configuration = yaml.load(working_file)
        self.logging.debug(self.dft_configuration)

        # Check if path starts with ~ and need expension
        if self.dft_configuration["configuration"]["working_dir"][0] == "~" and self.dft_configuration["configuration"]["working_dir"][1] == "/":
          self.dft_configuration["configuration"]["working_dir"] = os.path.expanduser(self.dft_configuration["configuration"]["working_dir"])

        self.logging.debug(self.dft_configuration)

      # Close file when reading is done
#TODO      close(working_file)

    except OSError as exception:
      # Call clean up to umount /proc and /dev
      self.logging.critical("Error: %s - %s." % (exception.filename, exception.strerror))
      exit(1)

# -----------------------------------------------------------------------------
#
# Class ProjectDefinition
#
# -----------------------------------------------------------------------------
class ProjectDefinition(object):
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
  def __init__(self, filename=None):
    """
    """

    # Create the logger object
    self.logging = logging.getLogger()

    # Store the filename containing the whole project definition
    # Filename is mandatory, and is defaulted to project.yml if
    # not defined
    if filename is None:
      self.project_name = 'project.yml'
    else:
      self.project_name = filename

    # Timestamp is used to produce distinct directory in case of several
    # run, and also used to produce the serial number (/etc/dft_version)
    self.timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    # Create the object storing the DFT tool configuration
    self.dft = DftConfiguration()

    # Defines path for subcommand
    self.rootfs_base_workdir = None
    self.image_base_workdir = None
    self.bootloader_base_workdir = None
    self.firmware_base_workdir = None
    self.content_base_workdir = None

    # Defines member variables
    self.target_arch = None
    self.target_version = None
    self.archive_filename = None
    self.rootfs_mountpoint = None
    self.firmware_directory = None
    self.firmware_filename = None
    self.init_filename = None
    self.stacking_script_filename = None

    self.rootfs_def = None
    self.bootloader_def = None
    self.check_def = None
    self.content_information_def = None
    self.firmware_def = None
    self.image_def = None
    self.project_base_workdir = None
    self.project_def = None
    self.repositories_def = None
    self.rootfs_generator_cachedirname = None
    self.stripping_def = None
    self.variables_def = None



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
    if "project_path" in self.project_def["configuration"]:
      filename = self.project_def["configuration"]["project_path"] + "/" + filename
    else:
      filename = os.path.dirname(self.project_name) + "/" + filename

# TODO add include in project file

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
# TODO : load and merge several confiuration files in the same dictionnary
      #
      # Load all the ub configuration files from disk
      #
      with open(self.project_name, 'r') as working_file:
        self.project_def = yaml.load(working_file)

        # Expand ~ in path since it is not done automagically by Python
        for key in {"dft_base", "project_path", "working_dir"}:
          # For iterate the key and check they are defined in the config file
          if key in self.project_def["configuration"]:
            # Then chek if the single value field starts by "~/"
            if self.project_def["configuration"][key][0] == "~" and self.project_def["configuration"][key][1] == "/":
              # If yes modifiy its value using expenduser ( replace ~ by /home/foo)
              self.project_def["configuration"][key] = os.path.expanduser(self.project_def["configuration"][key])

        # Expand ~ in path since it is not done automagically by Python
        for key in {"additional_roles"}:
          # For iterate the key and check they are defined in the config file
          if key in self.project_def["configuration"]:
            # Then iterate the list of values it contains
            for counter in range(len(self.project_def["configuration"][key])):
              # Then chek if the valuestarts by "~/"
              if self.project_def["configuration"][key][counter][0] == "~" and self.project_def["configuration"][key][counter][1] == "/":
                # If yes modifiy its value using expenduser ( replace ~ by /home/foo)
                self.project_def["configuration"][key][counter] = os.path.expanduser(self.project_def["configuration"][key][counter])

      # Load the repositories sub configuration files
      if "repositories" in self.project_def["project_definition"]:
        filename = self.generate_def_file_path(self.project_def["project_definition"]["repositories"][0])
        with open(filename, 'r') as working_file:
          self.repositories_def = yaml.load(working_file)

      # Load the rootfs sub configuration files
      if "rootfs" in self.project_def["project_definition"]:
        filename = self.generate_def_file_path(self.project_def["project_definition"]["rootfs"][0])
        with open(filename, 'r') as working_file:
          self.rootfs_def = yaml.load(working_file)

      # Load the firmware sub configuration files
      if "firmware" in self.project_def["project_definition"]:
        filename = self.generate_def_file_path(self.project_def["project_definition"]["firmware"][0])
        with open(filename, 'r') as working_file:
          self.firmware_def = yaml.load(working_file)

      # Load the bootloader sub configuration files
      if "bootloader" in self.project_def["project_definition"]:
        filename = self.generate_def_file_path(self.project_def["project_definition"]["bootloader"][0])
        with open(filename, 'r') as working_file:
          self.bootloader_def = yaml.load(working_file)

      # Load the image sub configuration files
      if "image" in self.project_def["project_definition"]:
        filename = self.generate_def_file_path(self.project_def["project_definition"]["image"][0])
        with open(filename, 'r') as working_file:
          self.image_def = yaml.load(working_file)

      # Load the check sub configuration files
      if "check" in self.project_def["project_definition"]:
        filename = self.generate_def_file_path(self.project_def["project_definition"]["check"][0])
        with open(filename, 'r') as working_file:
          self.check_def = yaml.load(working_file)

      # Load the stripping sub configuration files
      if "stripping" in self.project_def["project_definition"]:
        filename = self.generate_def_file_path(self.project_def["project_definition"]["stripping"][0])
        with open(filename, 'r') as working_file:
          self.stripping_def = yaml.load(working_file)

      # Load the check sub configuration files
      if "content_information" in self.project_def["project_definition"]:
        filename = self.generate_def_file_path(self.project_def["project_definition"]["content_information"][0])
        with open(filename, 'r') as working_file:
          self.content_information_def = yaml.load(working_file)

      # Load the list of variables files
      if "variables" in self.project_def["project_definition"]:
        filename = self.generate_def_file_path(self.project_def["project_definition"]["variables"][0])
        with open(filename, 'r') as working_file:
          self.variables_def = yaml.load(working_file)

      #
      # Once configuration have been loaded, compute the values of some
      # configuration variables
      #

      # Generate the cache archive filename
      if "rootfs_generator_cachedirname" in self.project_def["configuration"]:
        self.rootfs_generator_cachedirname = self.project_def["configuration"]["rootfs_generator_cachedirname"]
      else:
        self.logging.warning("configuration/rootfs_generator_cachedirname is not defined, using /tmp as default value")
        self.rootfs_generator_cachedirname = "/tmp/"

      if "working_dir" in self.project_def["configuration"]:
        self.project_base_workdir = self.project_def["configuration"]["working_dir"]
        self.project_base_workdir += "/" + self.project_def["configuration"]["project_name"]
      else:
        self.logging.warning("configuration/working_dir is not defined, using /tmp/dft as default value")
        self.project_base_workdir = "/tmp/dft/"
        self.project_base_workdir += self.project_def["configuration"]["project_name"]

      # Defines path for subcommand
      self.rootfs_base_workdir = self.project_base_workdir + "/rootfs"
      self.image_base_workdir = self.project_base_workdir + "/image"
      self.bootloader_base_workdir = self.project_base_workdir + "/bootloader"
      self.firmware_base_workdir = self.project_base_workdir + "/firmware"
      self.content_base_workdir = self.project_base_workdir + "/content"

      # Retrieve the target architecture
# TODO : handle multiple archs
      self.target_arch = self.project_def["project_definition"]["architectures"][0]

      # Target version to use when building the debootstrap. It has to be
      # a Debian version (jessie, stretch, etc.)
# TODO : handle multiple version
      self.target_version = self.rootfs_def["target_versions"][0]

      # Generate the archive filename
# TODO : handle multiple archs / version
      self.archive_filename = self.rootfs_generator_cachedirname + "/" + self.target_arch
      self.archive_filename += "-" +  self.target_version + "-"
      self.archive_filename += self.project_def["configuration"]["project_name"]
      self.archive_filename += ".tar"

      # Generates the path to the rootfs mountpoint
      # Stores the path to the rootfs mountpoint used by debootstrap
      self.rootfs_mountpoint = self.rootfs_base_workdir + "/" + self.target_arch
      self.rootfs_mountpoint += "-" + self.target_version

      # Generate the path where to store generated squashfs files
      self.firmware_directory = self.firmware_base_workdir + "/"
      self.firmware_directory += self.target_arch + "-" + self.target_version

      self.firmware_filename = self.firmware_directory + "/"
      self.firmware_filename += self.project_def["configuration"]["project_name"]
      self.firmware_filename += ".squashfs"

      self.init_filename = self.firmware_directory + "/init"
      self.stacking_script_filename = self.firmware_directory + "/dft_create_stack.sh"

    # Handle exception that may occur when trying to open unknown files
    except OSError as exception:
      # Just log and exit, nothing is mounted yet
      self.logging.critical("Error: %s - %s.", exception.filename, exception.strerror)
      exit(1)
