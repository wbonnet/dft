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
from enum import Enum
from datetime import datetime
import yaml


# -----------------------------------------------------------------------------
#
# class Key
#
# -----------------------------------------------------------------------------
class Key(Enum):
  """This class defines the valid keys to used to access infrmation from
  confiugration files. The keys are enumerated vlues defined by string. The string
  used are (understand 'must be') the same as the keys in yaml files.

  No string should be manipulated directly, only enum values
  """

  # Define each and every key and associated string used in the DFT tool

  ABSENT = "absent"
  ADDITIONAL_ROLES = "additional_roles"
  ALL_ROOT = "all_root"
  ALLOW_OPTIONAL = "allow_optional"
  ALLOWED = "allowed"
  ALLOWED_ARCH = "allowed_arch"
  ALLOWED_VERSION = "allowed_version"
  ANTIVIRUS = "antivirus"
  ARCH = "arch"
  ARCHITECTURE = "architecture"
  ARCHITECTURES = "architectures"
  ARCHIVE_FILENAME_EXTENSION = ".tar"
  ARM = "arm"
  ARMEL = "armel"
  ARMHF = "armhf"
  ASSEMBLE_FIRMWARE = "assemble_firmware"
  AUFS = "aufs"
  BLACKLISTED_ARCH = "blacklisted_arch"
  BLACKLISTED_VERSION = "blacklisted_version"
  BLOCK_SIZE = "block_size"
  BOOTLOADER = "bootloader"
  BOOTLOADER_WORKDIR = "bootloader"
  BUILD_BOOTLOADER = "build_bootloader"
  BUILD_FIRMWARE = "build_firmware"
  BUILD_IMAGE = "build_image"
  BUILD_ROOTFS = "build_rootfs"
  CHECK = "check"
  CHECK_ROOTFS = "check_rootfs"
  COMPRESSOR = "compressor"
  CONFIG_FILE = "config_file"
  CONFIGURATION = "configuration"
  CONTENT_INFORMATION = "content_information"
  CONTENT_WORKDIR = "content"
  CSV = "csv"
  DEBOOTSTRAP_REPOSITORY = "debootstrap_repository"
  DEBOOTSTRAP_TARGET = "minbase"
  DEFAULT_CONFIGURATION_FILE = "~/.dftrc"
  DEFAULT_PROJECT_FILE = "project.yml"
  DESCRIPTION = "description"
  DFT_BASE = "dft_base"
  DIRECTORIES = "directories"
  DIRECTORY = "directory"
  DISTRIBUTIONS = "distributions"
  EMPTY = "empty"
  EXPECTED_RESULT = "expected_result"
  FACTORY_SETUP = "factory_setup"
  FILE = "file"
  FILES = "files"
  FIRMWARE = "firmware"
  FIRMWARE_FILENAME_EXTESION = ".fw"
  FIRMWARE_WORKDIR = "firmware"
  FORBIDDEN = "forbidden"
  FORCE_UID = "force_uid"
  FORMAT = "format"
  GEN_ANTIVIRUS_INFO = "gen_antivirus_info"
  GEN_CONTENT_INFO = "generate_content_information"
  GEN_FILES_INFO = "gen_files_info"
  GEN_PACKAGES_INFO = "gen_packages_info"
  GEN_ROOTKIT_INFO = "generate_rootkit_information"
  GEN_SECURITY_INFO = "gen_security_info"
  GEN_VULNERABILITIES_INFO = "gen_vulnerabilities_info"
  GENERATE_DEB = "generate_deb"
  GENERATE_SRC = "generate_src"
  GENERATE_VALIDITY_CHECK = "generate_validity_check"
  GENERATOR_CACHE_DIR = "generator_cache_dir"
  GROUP = "group"
  HASH_METHOD = "hash_method"
  IMAGE = "image"
  IMAGE_WORKDIR = "image"
  INIT_FILENAME = "init_filename"
  INSTALL_MISSING_SOFTWARE = "install_missing_software"
  INSTALL_MSSING_SOFTWARE = "install_mssing_software"
  INSTALLATION_CONSTRAINT = "installation_constraint"
  INSTALLED_SIZE = "installed_size"
  JSON = "json"
  KEEP_BOOTSTRAP_FILES = "keep_bootstrap_files"
  KEEP_ROOTFS_HISTORY = "keep_rootfs_history"
  LABEL = "label"
  LABEL_RESULT_FAIL = "[FAIL]"
  LABEL_RESULT_OK = "[ OK ]"
  LAYOUT = "layout"
  LIMIT_TARGET_ARCH = "limit_target_arch"
  LIMIT_TARGET_VERSION = "limit_target_version"
  LOG_LEVEL = "log_level"
  LYNIS = "lynis"
  MANDATORY = "mandatory"
  MANDATORY_ONLY = "mandatory_only"
  MAX_VERSION = "max_version"
  MD5 = "md5"
  METHOD = "method"
  MIN_VERSION = "min_version"
  MODE = "mode"
  MOUNT_OPTIONS = "mount_options"
  MOUNTPOINT = "mountpoint"
  NAME = "name"
  NO_CONSTRAINT = "no_constraint"
  NO_DATABLOCK_COMPRESSION = "no_datablock_compression"
  NO_DUPICATE_CHECK = "no_dupicate_check"
  NO_EXPORTS = "no_exports"
  NO_FRAGMENTBLOCK_COMPRESSION = "no_fragmentblock_compression"
  NO_INODE_COMPRESSION = "no_inode_compression"
  NO_SPARE = "no_spare"
  NO_XATTRS_COMPRESSION = "no_xattrs_compression"
  NOPAD = "nopad"
  OPT_CONFIG_FILE = "--config-file"
  OPT_GEN_ANTIVIRUS_INFO = "--generate-antivirus-information"
  OPT_GEN_FILES_INFO = "--generate-files-information"
  OPT_GEN_PACKAGES_INFO = "--generate-packages-information"
  OPT_GEN_ROOTKIT_INFO = "--generate-rootkit-information"
  OPT_GEN_SECURITY_INFO = "--generate-security-information"
  OPT_GEN_VULNERABILITIES_INFO = "--generate-vulnerabilities-information"
  OPT_HELP_LABEL = "Command to execute"
  OPT_KEEP_BOOTSTRAP_FILES = "--keep-bootstrap-files"
  OPT_LIMIT_ARCH = "--limit-arch"
  OPT_LIMIT_VERSION = "--limit-version"
  OPT_LOG_LEVEL = "--log-level"
  OPT_OVERRIDE_DEBIAN_MIRROR = "--override-debian-mirror"
  OPT_PROJECT_FILE = "--project-file"
  OPT_UPDATE_CACHE_ARCHIVE = "--update-cache-archive"
  OPT_USE_CACHE_ARCHIVE = "--use-cache-archive"
  OUTPUT = "output"
  OUTPUT_PKG_ARCHITECTURE = "output_pkg_architecture"
  OUTPUT_PKG_DESCRIPTION = "output_pkg_description"
  OUTPUT_PKG_INSTALLED_SIZE = "output_pkg_installed_size"
  OUTPUT_PKG_MD5 = "output_pkg_md5"
  OUTPUT_PKG_NAME = "output_pkg_name"
  OUTPUT_PKG_SHA256 = "output_pkg_sha256"
  OUTPUT_PKG_SIZE = "output_pkg_size"
  OUTPUT_PKG_STATUS = "output_pkg_status"
  OUTPUT_PKG_VERSION = "output_pkg_version"
  OVERLAYFS = "overlayfs"
  OVERRIDE_DEBIAN_MIRROR = "override_debian_mirror"
  OWNER = "owner"
  PACKAGES = "packages"
  PARTITION = "partition"
  PATH = "path"
  PROJECT_DEFINITION = "project_definition"
  PROJECT_FILE = "project_file"
  PROJECT_NAME = "project.yml"
  PROJECT_PATH = "project_path"
  PROJECT_WORKDIR = "project_base_workdir"
  REMOVE_VALIDITY_CHECK = "remove_validity_check"
  REPOSITORIES = "repositories"
  RKHUNTER = "rkhunter"
  ROLES = "roles"
  ROOTFS = "rootfs"
  ROOTFS_DIR = "rootfs"
  ROOTKIT = "rootkit"
  SCAN = "scan"
  SECTIONS = "sections"
  SECURITY = "security"
  SHA1 = "sha1"
  SHA256 = "sha256"
  SIZE = "size"
  SKIP_MISSING_SOFTWARE = "skip_missing_software"
  SQUASHFS = "squashfs"
  SQUASHFS_FILE = "squashfs-file"
  STACK_DEFINITION = "stack_definition"
  STACK_ITEM = "stack_item"
  STACK_SCRIPT = "dft_stack_script.sh"
  STATUS = "status"
  STDOUT = "stdout"
  STRIP_ROOTFS = "strip_rootfs"
  STRIPPING = "stripping"
  SUITE = "suite"
  SYMLINK = "symlink"
  TARGET = "target"
  TARGET_PATH = "target_path"
  TARGET_VERSIONS = "target_versions"
  TMPFS = "tmpfs"
  TYPE = "type"
  UPDATE_CACHE_ARCHIVE = "update_cache_archive"
  UPDATE_DATABASE = "update_database"
  URL = "url"
  USE_CACHE_ARCHIVE = "use_cache_archive"
  USE_FRAGMENTS = "use_fragments"
  USE_HOST_AV = "use_host_av"
  UTF8 = "utf-8"
  VARIABLES = "variables"
  VERSION = "version"
  VULNERABILITIES = "vulnerabilities"
  WORKING_DIR = "working_dir"
  XATTRS = "xattrs"
  XML = "xml"
  YAML = "yaml"
  YML = "yml"

# TODO: add a method to initialize all defaut value and not do it into the code

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

    try:
      # Load it
      with open(self.project_name, 'r') as working_file:
        self.logging.debug("loading dft configuration : " + filename)
        self.dft_configuration = yaml.load(working_file)
        self.logging.debug(self.dft_configuration)

        # Check if path starts with ~ and need expension
        if self.dft_configuration[Key.CONFIGURATION.value][Key.WORKING_DIR.value][0] == "~" \
        and self.dft_configuration[Key.CONFIGURATION.value][Key.WORKING_DIR.value][1] == "/":
          self.dft_configuration[Key.CONFIGURATION.value][Key.WORKING_DIR.value] = \
                    os.path.expanduser(self.dft_configuration[Key.CONFIGURATION.value]\
                    [Key.WORKING_DIR.value])

        self.logging.debug(self.dft_configuration)

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
      self.project_name = Key.PROJECT_NAME.value
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
    self.target_arch = "unknown"
    self.target_version = "unknown"
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
    if "project_path" in self.project_def[Key.CONFIGURATION.value]:
      filename = self.project_def[Key.CONFIGURATION.value]["project_path"] + "/" + filename
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
        for key in {"dft_base", "project_path", Key.WORKING_DIR.value}:
          # For iterate the key and check they are defined in the config file
          if key in self.project_def[Key.CONFIGURATION.value]:
            # Then chek if the single value field starts by "~/"
            if self.project_def[Key.CONFIGURATION.value][key][0] == "~" and \
               self.project_def[Key.CONFIGURATION.value][key][1] == "/":
              # If yes modifiy its value using expenduser ( replace ~ by /home/foo)
              self.project_def[Key.CONFIGURATION.value][key] = \
                              os.path.expanduser(self.project_def[Key.CONFIGURATION.value][key])

        # Expand ~ in path since it is not done automagically by Python
        for key in {Key.ADDITIONAL_ROLES.value}:
          # For iterate the key and check they are defined in the config file
          if key in self.project_def[Key.CONFIGURATION.value]:
            # Then iterate the list of values it contains
            for counter in range(len(self.project_def[Key.CONFIGURATION.value][key])):
              # Then chek if the valuestarts by "~/"
              if self.project_def[Key.CONFIGURATION.value][key][counter][0] == "~" and \
                 self.project_def[Key.CONFIGURATION.value][key][counter][1] == "/":
                # If yes modifiy its value using expenduser ( replace ~ by /home/foo)
                self.project_def[Key.CONFIGURATION.value][key][counter] = \
                      os.path.expanduser(self.project_def[Key.CONFIGURATION.value][key][counter])

      # Load the repositories sub configuration files
      if Key.REPOSITORIES.value in self.project_def[Key.PROJECT_DEFINITION.value]:
        filename = self.generate_def_file_path(self.project_def[Key.PROJECT_DEFINITION.value]\
                                               [Key.REPOSITORIES.value][0])
        with open(filename, 'r') as working_file:
          self.repositories_def = yaml.load(working_file)

      # Load the rootfs sub configuration files
      if "rootfs" in self.project_def[Key.PROJECT_DEFINITION.value]:
        filename = self.generate_def_file_path(self.project_def[Key.PROJECT_DEFINITION.value]\
                                                               ["rootfs"][0])
        with open(filename, 'r') as working_file:
          self.rootfs_def = yaml.load(working_file)

      # Load the firmware sub configuration files
      if "firmware" in self.project_def[Key.PROJECT_DEFINITION.value]:
        filename = self.generate_def_file_path(self.project_def[Key.PROJECT_DEFINITION.value]\
                                                               ["firmware"][0])
        with open(filename, 'r') as working_file:
          self.firmware_def = yaml.load(working_file)

      # Load the bootloader sub configuration files
      if "bootloader" in self.project_def[Key.PROJECT_DEFINITION.value]:
        filename = self.generate_def_file_path(self.project_def[Key.PROJECT_DEFINITION.value]\
                                                               ["bootloader"][0])
        with open(filename, 'r') as working_file:
          self.bootloader_def = yaml.load(working_file)

      # Load the image sub configuration files
      if "image" in self.project_def[Key.PROJECT_DEFINITION.value]:
        filename = self.generate_def_file_path(self.project_def[Key.PROJECT_DEFINITION.value]\
                                                               ["image"][0])
        with open(filename, 'r') as working_file:
          self.image_def = yaml.load(working_file)

      # Load the check sub configuration files
      if "check" in self.project_def[Key.PROJECT_DEFINITION.value]:
        filename = self.generate_def_file_path(self.project_def[Key.PROJECT_DEFINITION.value]\
                                                               ["check"][0])
        with open(filename, 'r') as working_file:
          self.check_def = yaml.load(working_file)

      # Load the stripping sub configuration files
      if "stripping" in self.project_def[Key.PROJECT_DEFINITION.value]:
        filename = self.generate_def_file_path(self.project_def[Key.PROJECT_DEFINITION.value]\
                                                               ["stripping"][0])
        with open(filename, 'r') as working_file:
          self.stripping_def = yaml.load(working_file)

      # Load the check sub configuration files
      if "content_information" in self.project_def[Key.PROJECT_DEFINITION.value]:
        filename = self.generate_def_file_path(self.project_def[Key.PROJECT_DEFINITION.value]\
                                                               ["content_information"][0])
        with open(filename, 'r') as working_file:
          self.content_information_def = yaml.load(working_file)

      # Load the list of variables files
      if "variables" in self.project_def[Key.PROJECT_DEFINITION.value]:
        filename = self.generate_def_file_path(self.project_def[Key.PROJECT_DEFINITION.value]\
                                                               ["variables"][0])
        with open(filename, 'r') as working_file:
          self.variables_def = yaml.load(working_file)

      #
      # Once configuration have been loaded, compute the values of some
      # configuration variables
      #

      # Generate the cache archive filename
      if "rootfs_generator_cachedirname" in self.project_def[Key.CONFIGURATION.value]:
        self.rootfs_generator_cachedirname = self.project_def[Key.CONFIGURATION.value]\
                                                             ["rootfs_generator_cachedirname"]
      else:
        self.logging.debug("configuration/rootfs_generator_cachedirname is not defined, using /tmp\
                            as default value")
        self.rootfs_generator_cachedirname = "/tmp/"

      if Key.WORKING_DIR.value in self.project_def[Key.CONFIGURATION.value]:
        self.project_base_workdir = self.project_def[Key.CONFIGURATION.value]\
                                                    [Key.WORKING_DIR.value]
        self.project_base_workdir += "/" + self.project_def[Key.CONFIGURATION.value]\
                                                           ["project_name"]
      else:
        self.logging.debug("configuration/working_dir is not defined, using /tmp/dft as default \
                            value")
        self.project_base_workdir = "/tmp/dft/"
        self.project_base_workdir += self.project_def[Key.CONFIGURATION.value]["project_name"]

      # Defines path for subcommand
      self.rootfs_base_workdir = self.project_base_workdir + "/rootfs"
      self.image_base_workdir = self.project_base_workdir + "/image"
      self.bootloader_base_workdir = self.project_base_workdir + "/bootloader"
      self.firmware_base_workdir = self.project_base_workdir + "/firmware"
      self.content_base_workdir = self.project_base_workdir + "/content"

      # Retrieve the target architecture
# TODO : handle multiple archs
      self.set_arch(self.project_def[Key.PROJECT_DEFINITION.value]\
                                    [Key.ARCHITECTURES.value][0])

      # Target version to use when building the debootstrap. It has to be
      # a Debian version (jessie, stretch, etc.)
        # Only set this variable if it is not defined. If it is defined, it means it has been
        # overriden from command line.
        # TODO seems not so clean... should be refactored
      self.set_version(self.rootfs_def["target_versions"][0])

      # Defines the full path and filename to the firmware
      self.firmware_filename = self.firmware_directory + "/"
      self.firmware_filename += self.project_def[Key.CONFIGURATION.value]["project_name"]
      self.firmware_filename += ".squashfs"

      # Defines the full path and filename to the init used by firmware
      self.init_filename = self.firmware_directory + "/init"
      self.stacking_script_filename = self.firmware_directory + "/dft_create_stack.sh"

    # Handle exception that may occur when trying to open unknown files
    except OSError as exception:
      # Just log and exit, nothing is mounted yet
      self.logging.critical("Error: %s - %s.", exception.filename, exception.strerror)
      exit(1)

  # ---------------------------------------------------------------------------
  #
  # set_version
  #
  # ---------------------------------------------------------------------------
  def set_version(self, version):
    """ This method set the version attribute, and all the attributes computed
    using version value. This method should be rewritten to handle building
    several version at a time.
    """

    # Defines the version attribute
    self.target_version = version

    # Generate the archive filename
# TODO : handle multiple archs / version
    self.archive_filename = self.rootfs_generator_cachedirname + "/" + self.target_arch
    self.archive_filename += "-" +  self.target_version + "-"
    self.archive_filename += self.project_def[Key.CONFIGURATION.value]["project_name"]
    self.archive_filename += ".tar"

    # Generates the path to the rootfs mountpoint
    # Stores the path to the rootfs mountpoint used by debootstrap
    self.rootfs_mountpoint = self.rootfs_base_workdir + "/" + self.target_arch
    self.rootfs_mountpoint += "-" + self.target_version

    # Generate the path where to store generated squashfs files
    self.firmware_directory = self.firmware_base_workdir + "/"
    self.firmware_directory += self.target_arch + "-" + self.target_version

  # ---------------------------------------------------------------------------
  #
  # set_arch
  #
  # ---------------------------------------------------------------------------
  def set_arch(self, arch):
    """ This method set the arch attribute, and all the attributes computed
    using arch value. This method should be rewritten to handle building
    several version at a time.
    """

    # Defines the arch attribute
    self.target_arch = arch

    # Generate the archive filename
# TODO : handle multiple archs / version
    self.archive_filename = self.rootfs_generator_cachedirname + "/" + self.target_arch
    self.archive_filename += "-" +  self.target_version + "-"
    self.archive_filename += self.project_def[Key.CONFIGURATION.value]["project_name"]
    self.archive_filename += ".tar"

    # Generates the path to the rootfs mountpoint
    # Stores the path to the rootfs mountpoint used by debootstrap
    self.rootfs_mountpoint = self.rootfs_base_workdir + "/" + self.target_arch
    self.rootfs_mountpoint += "-" + self.target_version

    # Generate the path where to store generated squashfs files
    self.firmware_directory = self.firmware_base_workdir + "/"
    self.firmware_directory += self.target_arch + "-" + self.target_version
