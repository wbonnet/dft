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
class DftConfiguration:
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
    if filename == None:
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

  # ---------------------------------------------------------------------------
  #
  # load_configuration
  #
  # ---------------------------------------------------------------------------
  def load_configuration(self, filename=None):

# TODO handle filename
    try:
      # Load it
      with open(self.project_name, 'r') as f:
        self.logging.debug("loading dft configuration : " + filename)
        self.dft_configuration = yaml.load(f)
        self.logging.debug(self.dft_configuration)

        # Check if path starts with ~ and need expension
        if self.dft_configuration["configuration"]["working_dir"][0] == "~" and self.dft_configuration["configuration"]["working_dir"][1] == "/":
          dft_configuration["configuration"]["working_dir"] = os.path.expanduser(dft_configuration["configuration"]["working_dir"])

        self.logging.debug(self.dft_configuration)

    except FileNotFoundError as e:
      # Call clean up to umount /proc and /dev
      self.logging.critical("Error: %s - %s." % (e.filename, e.strerror))
      exit(1)

# -----------------------------------------------------------------------------
#
# Class ProjectDefinition
#
# -----------------------------------------------------------------------------
class ProjectDefinition:
  """This class defines a project. A project holds all the information used
  to produce the different object created by DFT (baseos, modulations, 
  firmware, bootlader, etc.).

  Project is an aggregation of several dedicated configuration and
  definition object. It also includes tool configuration by itself.
  """ 

  # ---------------------------------------------------------------------------
  #
  # __init__
  #
  # ---------------------------------------------------------------------------
  def __init__(self, filename = None):
    """
    """

    # Create the logger object
    self.logging = logging.getLogger()

    # Store the filename containing the whole project definition
    # Filename is mandatory, and is defaulted to project.yml if 
    # not defined
    if (filename == None):
      self.project_name = 'project.yml'
    else:
      self.project_name = filename

    # Timestamp is used to produce distinct directory in case of several
    # run, and also used to produce the serial number (/etc/dft_version)
    self.timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    # Create the object storing the DFT tool configuration
    self.dft = DftConfiguration()

    # Defines path for subcommand
    self.rootfs_base_workdir     = ""
    self.image_base_workdir      = ""
    self.bootloader_base_workdir = ""
    self.firmware_base_workdir   = ""
    self.content_base_workdir    = ""


  # ---------------------------------------------------------------------------
  #
  # genereate_definition_file_path
  #
  #   This method generates the complete path to sub configuration files
  #   This files are referenced in the project configuration file, and are
  #   supposed to be in the same folder as the project file
  #
  #   A "project_path' can be defined in the project file. If defined, the 
  #   files are loaded from this place. If not, they are loaded from the 
  #   directory containing the project file being used.
  #
  # ---------------------------------------------------------------------------
  def genereate_definition_file_path(self, filename):
    
    # Check if the project path is defined into the project file
    if "project_path" in self.project_definition["configuration"]: 
        filename = self.project_definition["configuration"]["project_path"] + "/" + filename
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
  def load_definition(self, filename = None):

    # Test if the filename has been redefinied
    if (filename != None):
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
      with open(self.project_name, 'r') as f:
        self.project_definition = yaml.load(f)   

        # Expand ~ in path since it is not done automagically by Python
        for key in { "dft_base", "project_path", "working_dir", "additional_roles" }:
          if key in self.project_definition["configuration"]:
            if self.project_definition["configuration"][key][0] == "~" and self.project_definition["configuration"][key][1] == "/":         
              self.project_definition["configuration"][key] = os.path.expanduser(self.project_definition["configuration"][key])

      # Load the repositories sub configuration files
      if "repositories" in self.project_definition["project-definition"]:
        filename = self.genereate_definition_file_path(self.project_definition["project-definition"]["repositories"][0])
        with open(filename, 'r') as f:
          self.repositories_definition = yaml.load(f)   

      # Load the baseos sub configuration files
      if "baseos" in self.project_definition["project-definition"]:
        filename = self.genereate_definition_file_path(self.project_definition["project-definition"]["baseos"][0])
        with open(filename, 'r') as f:
          self.baseos_definition = yaml.load(f)   
      
      # Load the firmware sub configuration files
      if "firmware" in self.project_definition["project-definition"]:
        filename = self.genereate_definition_file_path(self.project_definition["project-definition"]["firmware"][0])
        with open(filename, 'r') as f:
          self.firmware_definition = yaml.load(f)   
      
      # Load the bootloader sub configuration files
      if "bootloader" in self.project_definition["project-definition"]:
        filename = self.genereate_definition_file_path(self.project_definition["project-definition"]["bootloader"][0])
        with open(filename, 'r') as f:
          self.bootloader_definition = yaml.load(f)   
     
      # Load the image sub configuration files
      if "image" in self.project_definition["project-definition"]:
        filename = self.genereate_definition_file_path(self.project_definition["project-definition"]["image"][0])
        with open(filename, 'r') as f:
          self.image_definition = yaml.load(f)   

      # Load the check sub configuration files
      if "check" in self.project_definition["project-definition"]:
        filename = self.genereate_definition_file_path(self.project_definition["project-definition"]["check"][0])
        with open(filename, 'r') as f:
          self.check_definition = yaml.load(f)   

      # Load the stripping sub configuration files
      if "stripping" in self.project_definition["project-definition"]:
        print(self.project_definition["project-definition"]["stripping"])            
        filename = self.genereate_definition_file_path(self.project_definition["project-definition"]["stripping"][0])
        with open(filename, 'r') as f:
          self.stripping_definition = yaml.load(f)   

      # Load the check sub configuration files
      if "content-information" in self.project_definition["project-definition"]:
        filename = self.genereate_definition_file_path(self.project_definition["project-definition"]["content-information"][0])
        with open(filename, 'r') as f:
          self.content_information_definition = yaml.load(f)   

      # Load the list of variables files
      if "variables" in self.project_definition["project-definition"]:
        filename = self.genereate_definition_file_path(self.project_definition["project-definition"]["variables"][0])
        with open(filename, 'r') as f:
          self.variables_definition = yaml.load(f)   
     

      #
      # Once configuration have been loaded, compute the values of some
      # configuration variables
      #

      # Generate the cache archive filename
      if "rootfs_generator_cachedir" in self.project_definition["configuration"]:
        self.rootfs_generator_cachedir = self.project_definition["configuration"]["rootfs_generator_cachedir"]
      else:
        self.logging.warning("configuration/rootfs_generator_cachedir is not defined, using /tmp as default value")
        self.rootfs_generator_cachedir = "/tmp/"

      if "working_dir" in self.project_definition["configuration"]:
        self.project_base_workdir = self.project_definition["configuration"]["working_dir"] + "/" + self.project_definition["configuration"]["project_name"]
      else:
        self.logging.warning("configuration/working_dir is not defined, using /tmp/dft as default value")
        self.project_base_workdir = "/tmp/dft/" + self.project_definition["configuration"]["project_name"]

      # Defines path for subcommand
      self.rootfs_base_workdir     = self.project_base_workdir + "/rootfs"
      self.image_base_workdir      = self.project_base_workdir + "/image"
      self.bootloader_base_workdir = self.project_base_workdir + "/bootloader"
      self.firmware_base_workdir   = self.project_base_workdir + "/firmware"
      self.content_base_workdir    = self.project_base_workdir + "/content"

      # Retrieve the target architecture
# TODO : handle multiple archs
      self.target_arch = self.project_definition["project-definition"]["architectures"][0]

      # Target version to use when building the debootstrap. It has to be
      # a Debian version (jessie, stretch, etc.)
# TODO : handle multiple version
      self.target_version = self.baseos_definition["target-versions"][0]
      
      # Generate the archive filename
# TODO : handle multiple archs / version
      self.archive_filename = self.rootfs_generator_cachedir + "/" + self.target_arch + "-" +  self.target_version + "-" + self.project_definition["configuration"]["project_name"] + ".tar"

      # Generates the path to the rootfs mountpoint
      # Stores the path to the rootfs mountpoint used by debootstrap
      self.rootfs_mountpoint = self.rootfs_base_workdir + "/" + self.target_arch + "-" + self.target_version

      # Generate the path where to store generated squashfs files
      self.firmware_directory = self.firmware_base_workdir + "/" + self.target_arch + "-" + self.target_version
      self.firmware_filename =  self.firmware_directory + "/" + self.project_definition["configuration"]["project_name"] + ".squashfs"

    # Handle exception that may occur when trying to open unknown files 
    except FileNotFoundError as exception:
        # Just log and exit, nothing is mounted yet
        self.logging.critical("Error: %s - %s." % (exception.filename, exception.strerror))
        exit(1)
