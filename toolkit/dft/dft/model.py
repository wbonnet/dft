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

from datetime import datetime

# -------------------------------------------------------------------------
#
# class DftConfiguration
#
# -------------------------------------------------------------------------
class DftConfiguration: 
  """This class defines default configuration for the DFT toolchain

  The tool configuration contains environment variables used to define 
  information such as default root working path, cache directories, etc.

  The values stored in this object are read from the following sources, 
  in order of priority (from the highest priority to the lowest).
  """

  # -------------------------------------------------------------------------
  #
  # __init__
  #
  # -------------------------------------------------------------------------
  def __init__(self, filename = None):
    """
    """

    # Default configuration file to use if none is provided through the cli
    if filename == None:
      self.configuration_filename = "~/.dftrc"
    else:
      self.configuration_filename = filename

    # Boolean used to flag if the cache archive should used instead 
    # of doing a real debootstrap installation
    self.use_rootfs_cache = False

    # Boolean used to flag if the cache archive should used updated
    # after doing a real debootstrap installation
    self.update_rootfs_cache = False

    # Current log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    # TODO : default should be changed to INFO
    self.log_level = "DEBUG"

    # Path to the installation of the DFT ansible roles
    # TODO : change to some place under /usr/share once packaging will be done
    self.dft_source_path = "/home/william/Devel/dft/toolkit/ansible"

    # Debootstrap target to use (minbase or buildd)
    self.debootstrap_target = "minbase"

    # Path to the default directory ued to store rootfs and cache archives
    # It defaults to /tmp
    # TODO : This may lead to full file system, should be changed, may be
    # a mandatory value in the config file ? => change to None
    self.working_directory = None
   
  # -------------------------------------------------------------------------
  #
  # load_configuration
  #
  # -------------------------------------------------------------------------
  def load_configuration(self, filename = None):
    # Check that the filename has been passed either now or when calling init
    # Check that the file exist
    # Load it
    pass



# -------------------------------------------------------------------------
#
# Class ProjectDefinition
#
# -------------------------------------------------------------------------
class ProjectDefinition :
  """This class defines a project. A project holds all the information used
  to produce the different object created by DFT (baseos, modulations, 
  firmware, bootlader, etc.).

  Project is an aggregation of several dedicated configuration and
  definition object. It also includes tool configuration by itself.
  """ 

  # -------------------------------------------------------------------------
  #
  # __init__
  #
  # -------------------------------------------------------------------------
  def __init__(self, filename = None):
      """
      """

      # Store the filename containing the whole project definition
      # Filename is mandatory, and cannot be defaulted
      self.filename = filename

      # Timestamp is used to produce distinct directory in case of several
      # run, and also used to produce the serial number (/etc/dft_version)
      self.timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

      # Create the object storing the DFT tool configuration
      self.dft = DftConfiguration()

      # Create the object storing the baseos definition
      self.baseos = BaseosDefinition()

      # Create the object storing the firmware definition
      self.firmware = FirmwareDefinition()



      # Target version to use when building the debootstrap. It has to be
      # a Debian version (jessie, stretch, etc.)
      self.target_version = "stretch"

      # Stores the target architecture
      # TODO should we have a list here ? 
      self.target_arch = "amd64"

      # Name of the current baseos being produced. Used in rootfs mount
      # point path and archive name generation
      # TODO temporary values
      self.target_name = "test"

      # TODO temporary values
      self.dft_additional_path =  [ "/tmp/dft-additional" ]
      self.dft_ansible_targets = [ "test" ]

      # TODO 
      # Generate the cache archive filename
      self.rootfs_generator_cachedir = "/tmp/dft"
      self.rootfs_base_workdir = "/tmp/dft/rootfs_mountpoint"
      self.archive_filename = self.rootfs_generator_cachedir + "/" + self.target_arch + "-" +  self.target_version + "-" +  self.target_name + ".tar"

      # TODO 
      # Generates the path to the rootfs mountpoint
      rootfs_image_name   = self.target_arch + "-" + self.target_version + "-" + self.timestamp

      # TODO
      # Stores the path to the rootfs mountpoint used by debootstrap
      self.rootfs_mountpoint = self.rootfs_base_workdir + "/" + rootfs_image_name
  
  # -------------------------------------------------------------------------
  #
  # load_definition
  #
  # -------------------------------------------------------------------------
  def load_definition(self, filename = None):
    # Check that the filename has been passed either now or when calling init
    # Check that the file exist
    # Load it
    # Load the sub config files
    pass
#il faut
#la liste des prod targets a faire
#le repertoire de travail
#le repertoire de cache ?



# -------------------------------------------------------------------------
#
# BaseosDefinition
#
# -------------------------------------------------------------------------
class BaseosDefinition :
  """This class contains the definition of a baseos rootfs. It includes
  information about everything that is used either to configure its 
  specific build environment, or about things to include inside the firmware
  """ 

  # -------------------------------------------------------------------------
  #
  # __init__
  #
  # -------------------------------------------------------------------------
  def __init__(self, filename = None):
    """
    """

    # Store the filename containing the baseos rootfs definition
    # Filename is mandatory, and cannot be defaulted, but the same file
    # can be use to initialize several objects
    self.filename = filename

    # Default mirror to use. It has to be the URL of a valid Debian mirror
    # It is used by debootstrap as its sources of packages.
    self.pkg_archive_url = "http://mirrors/debian"

    # TODO Temporary until file parsing is fixed
    # TODO Should be a list
    self.debian_mirror_url  = "http://mirrors"

  # -------------------------------------------------------------------------
  #
  # load_definition
  #
  # -------------------------------------------------------------------------
  def load_definition(self, filename = None):
    # Check that the filename has been passed either now or when calling init
    # Check that the file exist
    # Load it
    pass


# -------------------------------------------------------------------------
#
# FirmwareDefinition
#
# -------------------------------------------------------------------------
class FirmwareDefinition :
  """This class contains the definition of a firmware. It includes
  information about which rootfs should be used, how many squashfs have to 
  be produced, their content, generation option etc.

  This class also defines the configuration of the /firmware loader/, which
  is the tool used on the target to created the stacked overlayfs
  """ 

  # -------------------------------------------------------------------------
  #
  # __init__
  #
  # -------------------------------------------------------------------------
  def __init__(self, filename = None):
      """
      """

      # Store the filename containing the firmware definition
      # Filename is mandatory, and cannot be defaulted, but the same file
      # can be use to initialize several objects
      self.filename = filename

  # -------------------------------------------------------------------------
  #
  # load_definition
  #
  # -------------------------------------------------------------------------
  def load_definition(self, filename = None):
    # Check that the filename has been passed either now or when calling init
    # Check that the file exist
    # Load it
    pass
