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

""" This module contains the functionnalities needed to create a squashfs compressed file
from a rootfs. The squashfs file contains hte operating system, or configuration files, or
anything you decide. They can be stacked in memory to create the read only operating system.
"""

import logging
import os
from shutil import rmtree
from dft.cli_command import CliCommand
from dft.model import Key

#
#    Class BuildFirmware
#
class BuildFirmware(CliCommand):
  """This class implements method needed to create the squashfs file(s) used
  to storefirmware content
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

  # -------------------------------------------------------------------------
  #
  # build_firmware
  #
  # -------------------------------------------------------------------------
  def build_firmware(self):
    """This method implement the business logic of firmware generation.
    Firmware is  squashfs file containing the rootfs generated previously.

    Current version produce only one squashfs file. Algorith is basic...
      . Create target directory if missing
      . Remove existing file
      . Generate the mksquashfs command and add options
      . That's all
    """

    # Check that there is a firmware configuration file first
    if self.project.firmware is None:
      self.project.logging.critical("The firmware configuration file is not defined in project")
      exit(1)

    # Ensure firmware generation path exists and is a dir
    if not os.path.isdir(self.project.get_rootfs_mountpoint()):
      logging.critical("The rootfs directory does not exist (" +
                       self.project.get_rootfs_mountpoint() + ")")
      exit(1)

    # Remove existing firmware if needed, and all the files that may be in this directory
    # FIXME: Check that bad configuration cannot destroy local machine
    if os.path.isdir(self.project.get_firmware_directory()):
      self.project.logging.info("Recreating the firmware output directory " +
                                self.project.get_firmware_directory())
      rmtree(self.project.get_firmware_directory())

    # Ensure firmware generation path exists and is a dir
    os.makedirs(self.project.get_firmware_directory())

    # Generate the squashfs files
    self.create_squashfs_files()

    # Generate checksums for squashfs_files
    self.create_squashfs_checksums()


  # -------------------------------------------------------------------------
  #
  # create_squashfs_checksums
  #
  # -------------------------------------------------------------------------
  def create_squashfs_checksums(self):
    """This method generates the checksum files (MD5 SHA1 or SHA256) according
    to the security options defined in the firmware section of the project.

    The algorith to use is defined by the security:hash-method key
    """

    # Test if the security section is defined
    if Key.SECURITY.value in self.project.firmware:
      # Yes, thus test if the hash-method is defined. If not defined, default
      # value is applied. Default value is "no hash"
      if Key.HASH_METHOD.value in self.project.firmware[Key.SECURITY.value]:
        # Convert hash-method to lower case in order to use it as command prefix
        self.project.firmware[Key.SECURITY.value][Key.HASH_METHOD.value] = self.project.\
                                    firmware[Key.SECURITY.value][Key.HASH_METHOD.value].lower()

        # Check that the algorith is valid (valid values are md5 sha1 sha224 sha256 sha384 sha512)
        if self.project.firmware[Key.SECURITY.value][Key.HASH_METHOD.value] in \
                                    [Key.MD5.value, Key.SHA1.value, Key.SHA224.value, \
                                     Key.SHA256.value, Key.SHA384, Key.SHA512]:
          # Output some fancy logs :)
          self.project.logging.info("Generating hash file " + self.project.firmware_filename + "." +
                                    self.project.firmware[Key.SECURITY.value]\
                                                             [Key.HASH_METHOD.value])

          # Generate the hash tool call
          cmd = self.project.firmware[Key.SECURITY.value][Key.HASH_METHOD.value] + "sum " + '"'
          cmd += self.project.firmware_filename + '" > "' + self.project.firmware_filename
          cmd += "." + self.project.firmware[Key.SECURITY.value][Key.HASH_METHOD.value] + '"'

          # Execute the hash generation command
          self.execute_command(cmd)

        # Algorithm is unknown, output an error and exit
        else:
          self.project.logging.error("The hash-method is unknown (" +
                                     self.project.firmware[Key.SECURITY.value]\
                                                              [Key.HASH_METHOD.value] + ")")
          exit(1)

      # Not defined, thus no hash generated,just log it
      else:
        self.project.logging.info("The key hash-method is not defined under security in this" +
                                  " firmware definition. No hash produced")
    else:
      self.project.logging.info("The security section is not defined under security in this" +
                                " firmware definition. No hash produced")



  # -------------------------------------------------------------------------
  #
  # create_squashfs_files
  #
  # -------------------------------------------------------------------------
  def create_squashfs_files(self):
    """This method implement the creation of squashfs files. It calls mksquash
    tool from comand line (by generating the call using all options from config)
    usiness logic of firmware generation.
    """

    # Deactivate too_many-branches since we want it to be written this way
    # pylint: disable=too-many-branches

    # Output some fancy logs :)
    self.project.logging.info("Generating " + self.project.firmware_filename)

    # Create a new squashfs file from the rootfs path
    cmd = 'mksquashfs "' +  self.project.get_rootfs_mountpoint() + '" "'
    cmd += self.project.firmware_filename + '"'

    # Append arguments if defined in the configuration file
    if "block_size" in self.project.firmware["configuration"]:
      cmd += ' -b ' + self.project.firmware["configuration"]["block_size"]

    if "compressor" in self.project.firmware["configuration"]:
      cmd += ' -comp ' + self.project.firmware["configuration"]["compressor"]

    if "no_exports" in self.project.firmware["configuration"]:
      if self.project.firmware["configuration"]["no_exports"]:
        cmd += ' -no-exports '

    if "no_spare" in self.project.firmware["configuration"]:
      cmd += ' -no-spare '

    if "xattrs" in self.project.firmware["configuration"]:
      if self.project.firmware["configuration"]["xattrs"]:
        cmd += ' -xattrs '
      if not self.project.firmware["configuration"]["xattrs"]:
        cmd += ' -no-xattrs '

    if "no_inode_compression" in self.project.firmware["configuration"]:
      cmd += ' -noI '

    if "no_datablock_compression" in self.project.firmware["configuration"]:
      cmd += ' -noD '

    if "no_fragmentblock_compression" in self.project.firmware["configuration"]:
      cmd += ' -noF '

    if "no_xattrs_compression" in self.project.firmware["configuration"]:
      cmd += ' -noX '

    if "use_fragments" in self.project.firmware["configuration"]:
      if self.project.firmware["configuration"]["use_fragments"]:
        cmd += ' -always_use_fragments '
      if not self.project.firmware["configuration"]["use_fragments"]:
        cmd += ' -no_fragments '

    if "no_duplicate_check" in self.project.firmware["configuration"]:
      if self.project.firmware["configuration"]["no_duplicate_check"]:
        cmd += ' -no-duplicates '

    if "all_root" in self.project.firmware["configuration"]:
      if self.project.firmware["configuration"]["all_root"]:
        cmd += ' -all-root '

    if "force_uid" in self.project.firmware["configuration"]:
      cmd += ' -force-uid '
      cmd += self.project.firmware["configuration"]["force_uid"]

    if "force_gid" in self.project.firmware["configuration"]:
      cmd += ' -force-gid '
      cmd += self.project.firmware["configuration"]["force_gid"]

    if "nopad" in self.project.firmware["configuration"]:
      if self.project.firmware["configuration"]["nopad"]:
        cmd += ' -nopad '

    self.execute_command(cmd)

    # Final log
    logging.info("Firmware has been successfully generated into : "\
                 + self.project.firmware_filename)
