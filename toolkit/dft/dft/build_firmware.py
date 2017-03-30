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
from cli_command import CliCommand

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
    if self.project.firmware_def is None:
      self.project.logging.critical("The firmware configuration file is not defined in project")
      exit(1)

    # Ensure firmware generation path exists and is a dir
    if not os.path.isdir(self.project.rootfs_mountpoint):
      logging.critical("The rootfs directory does not exist (" +
                       self.project.rootfs_mountpoint + ")")
      exit(1)

    # Ensure firmware generation path exists and is a dir
    if not os.path.isdir(self.project.firmware_directory):
      os.makedirs(self.project.firmware_directory)

    # Remove existing firmware if needed
    if os.path.isfile(self.project.firmware_filename):
      os.remove(self.project.firmware_filename)

    # Create a new squashfs file from the rootfs path
    sudo_command = 'mksquashfs "' +  self.project.rootfs_mountpoint + '" "'
    sudo_command += self.project.firmware_filename + '"'

    # Append arguments if defined in the configuration file
    if "block_size" in self.project.firmware_def["configuration"]:
      sudo_command += ' -b ' + self.project.firmware_def["configuration"]["block_size"]

    if "compressor" in self.project.firmware_def["configuration"]:
      sudo_command += ' -comp ' + self.project.firmware_def["configuration"]["compressor"]

    if "no_exports" in self.project.firmware_def["configuration"]:
      if self.project.firmware_def["configuration"]["no_exports"]:
        sudo_command += ' -no-exports '

    if "no_spare" in self.project.firmware_def["configuration"]:
      sudo_command += ' -no-spare '

    if "xattrs" in self.project.firmware_def["configuration"]:
      if self.project.firmware_def["configuration"]["xattrs"]:
        sudo_command += ' -xattrs '
      if not self.project.firmware_def["configuration"]["xattrs"]:
        sudo_command += ' -no-xattrs '

    if "no_inode_compression" in self.project.firmware_def["configuration"]:
      sudo_command += ' -noI '

    if "no_datablock_compression" in self.project.firmware_def["configuration"]:
      sudo_command += ' -noD '

    if "no_fragmentblock_compression" in self.project.firmware_def["configuration"]:
      sudo_command += ' -noF '

    if "no_xattrs_compression" in self.project.firmware_def["configuration"]:
      sudo_command += ' -noX '

    if "use_fragments" in self.project.firmware_def["configuration"]:
      if self.project.firmware_def["configuration"]["use_fragments"]:
        sudo_command += ' -always_use_fragments '
      if not self.project.firmware_def["configuration"]["use_fragments"]:
        sudo_command += ' -no_fragments '

    if "no_duplicate_check" in self.project.firmware_def["configuration"]:
      if self.project.firmware_def["configuration"]["no_duplicate_check"]:
        sudo_command += ' -no-duplicates '

    if "all_root" in self.project.firmware_def["configuration"]:
      if self.project.firmware_def["configuration"]["all_root"]:
        sudo_command += ' -all-root '

    if "force_uid" in self.project.firmware_def["configuration"]:
      sudo_command += ' -force-uid '
      sudo_command += self.project.firmware_def["configuration"]["force_uid"]

    if "force_gid" in self.project.firmware_def["configuration"]:
      sudo_command += ' -force-gid '
      sudo_command += self.project.firmware_def["configuration"]["force_gid"]

    if "nopad" in self.project.firmware_def["configuration"]:
      if self.project.firmware_def["configuration"]["nopad"]:
        sudo_command += ' -nopad '

    self.execute_command(sudo_command)

    # Final log
    logging.info("Firmware has been successfully generated into : "\
                 + self.project.firmware_filename)

# TODO : add control hash and signature according to configuration file options
