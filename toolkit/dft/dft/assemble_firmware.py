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

""" This modules implements the functionnalities used to create the initramfs in charge of
setting up the firmware in memory at system boot.
"""

import logging
import os
import tempfile
import datetime
from cli_command import CliCommand


#
#    Class AssembleFirmware
#
class AssembleFirmware(CliCommand):
  """This class implements method needed to assemble the toolchain used to
  assemble firmware inmemory when system is booting.

  Firmware assembling incudes the tasks of generating configuration files
  for sqashfs stacking and initramfs generation. It also includes the
  creation of the script used to handles reboot to preious version, and
  integrity check at start.
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
  # assemble_firmware
  #
  # -------------------------------------------------------------------------
  def assemble_firmware(self):
    """This method implement the business logic of firmware assembling.

    Assembling a firmware, use as input the firmware file created from a
    baseos and then generate the configuration files used to loading after
    booting. The configuration is used to define how the filesystems are
    stacked, what should be the physical partitionning, ciphering, etc.

    It calls dedicated method for each step. The main steps are :
    .
    """

    # Check that there is a firmware configuration file first
    if self.project.firmware_definition is None:
      self.project.logging.critical("The firmware configuration file is not defined in project file")
      exit(1)

    # Check that the layout is available from the firmware configuration file
    if "layout" not in self.project.firmware_definition:
      self.project.logging.critical("The firmware layout is not defined in configuration file")
      exit(1)

    # Check that the stacking method is available from the firmware configuration file
    if "method" not in self.project.firmware_definition["layout"]:
      self.project.logging.critical("The firmware stacking method is not defined")
      exit(1)

    # Ensure firmware generation path exists and is a dir
    if not os.path.isdir(self.project.firmware_directory):
      os.makedirs(self.project.firmware_directory)

    # Ensure firmware exists
    # TODO : iterate the list of squashfs files
    if not os.path.isfile(self.project.firmware_filename):
      logging.critical("The firmware does not exist (" +
                       self.project.firmware_filename + ")")
      exit(1)

    # Remove existing initscript if needed
    if os.path.isfile(self.project.init_filename):
      os.remove(self.project.init_filename)

    # Copy the init script to the target directory

    # Generate the stacking script
    self.generate_stack_script()



  # -------------------------------------------------------------------------
  #
  # generate_stack_script
  #
  # -------------------------------------------------------------------------
  def generate_stack_script(self):
    """This method implement the generation of the stacking script

    The stacking script is called in the initramfs by the init script. Stacking
    script is a shell scipt generated using the firmware.yml configuration
    as input. It provides th specific cod used to mount and stack the filesystms
    (using aufs or overlayfs).
    """

    # Generate the stacking script
        # configuration, then move  roles to the target rootfs
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as working_file:
      # Retrieve geenration date
      today = datetime.datetime.now()

      # Generate file header
      working_file.write("#\n")
      working_file.write("# DFT Create Stack\n")
      working_file.write("#\n")
      working_file.write("# This script has been generated automatically by the DFT toolkit.\n")
      working_file.write("# It is in charge of mounting and stacking the different items\n")
      working_file.write("# of the firmware.\n")
      working_file.write("#\n")
      working_file.write("# Generation date : " + today.strftime("%d/%m/%Y - %H:%M.%S") + "\n")
      working_file.write("#\n")
      working_file.write("\n")
    working_file.close()

    # Generate the common stuff. It includes mounting the target (used later for stacking them)
    self.generate_common_mount(working_file.name)

    # Call the method dedicated to the selected stacking method
    if self.project.firmware_definition["layout"]["method"] == "aufs":
      # Generate aufs stuff
      self.generate_aufs_stacking(working_file.name)
    elif self.project.firmware_definition["layout"]["method"] == "overlayfs":
      # Generate overlayfs stuff
      self.generate_overlayfs_stacking(working_file.name)
    else:
      # If we reach this code, then method was unknown
      self.project.logging.critical("Unknown stacking method " +
                                    self.project.firmware_definition["layout"]["method"])
      exit(1)

    # We are done with file generation, close it now

    # Generate the file path
    filepath = self.project.stacking_script_filename

    # Finally move the temporary file under the rootfs tree
    sudo_command = "mv -f " + working_file.name + " " + filepath
    self.execute_command(sudo_command)



  # -------------------------------------------------------------------------
  #
  # generate_common_mount
  #
  # -------------------------------------------------------------------------
  def generate_common_mount(self, working_file_name):
    """This method generates the command common to all the stacking methods.
    It includes creating the mount point and mount the partition and file
    systems.

    It takes as argument the output file opened by the calling method. This
    method only do output, the file is closed after the method returns.
    """

    # Reopen the working file
    working_file = open(working_file_name, "a")

    # Check that the stack definition is in the configuration file
    if "stack_definition" not in self.project.firmware_definition["layout"]:
      self.project.logging.critical("The stack definition is not in the configuration file")
      exit(1)

    # Create the workdir
    working_file.write("# Create the workdir directory\n")
    working_file.write("mkdir -p /mnt/dft/workdir\n")
    working_file.write("\n")

    # Iterates the stack items
    for item in self.project.firmware_definition["layout"]["stack_definition"]:
      # Generate the mount point creation code
      working_file.write("# Create the mount point for " + item["stack_item"]["type"] +
                         " '" + item["stack_item"]["name"] + "'\n")
      working_file.write("mkdir -p /mnt/dft/" + item["stack_item"]["name"] + "\n")
      working_file.write("\n")

      # Generate the mount commands
      working_file.write("# Mount item " + item["stack_item"]["type"] + " '" +
                         item["stack_item"]["name"] + "'\n")

      # Generate the tmpfs specific mount command
      if item["stack_item"]["type"] == "tmpfs":
        working_file.write("mount -t tmpfs ")

        # Is there some defined options ?
        if "mount_options" in item["stack_item"]:
          # Yes, then append the options to the command
          working_file.write("-o " + item["stack_item"]["mount_options"] + " ")

        # Complete the mount command
        working_file.write("tmpfs /mnt/dft/" + item["stack_item"]["name"] + "\n")
        working_file.write("mkdir /mnt/dft/" + item["stack_item"]["name"] + "/workdir\n")
        working_file.write("mkdir /mnt/dft/" + item["stack_item"]["name"] + "/mountpoint\n")

      # Generate the tmpfs specific mount command
      if item["stack_item"]["type"] == "squashfs":
        working_file.write("mount -t squashfs ")

        # Is there some defined options ?
        if "mount-options" in item["stack_item"]:
          # Yes, then append the options to the command
          working_file.write("-o " + item["stack_item"]["mount_options"] + " ")

        # Complete the mount command
        working_file.write(item["stack_item"]["squashfs_file"] + " /mnt/dft/" +
                           item["stack_item"]["name"] + " -o loop\n")

      # Generate the tmpfs specific mount command
      if item["stack_item"]["type"] == "partition":
        working_file.write("mount ")

        # Is there some defined options ?
        if "mount-options" in item["stack_item"]:
          # Yes, then append the options to the command
          working_file.write("-o " + item["stack_item"]["mount-options"] + " ")

        # Complete the mount command
        working_file.write(item["stack_item"]["partition"] + " /mnt/dft/" +
                           item["stack_item"]["name"] + "\n")

      working_file.write("\n")

    # We are done here, now close the file
    working_file.close()



  # -------------------------------------------------------------------------
  #
  # generate_overlayfs_stacking
  #
  # -------------------------------------------------------------------------
  def generate_overlayfs_stacking(self, working_file_name):
    """This method generates the command needed to stack the file systems
    using overlayfs.

    It takes as argument the output file opened by the calling method. This
    method only do output, the file is closed after the method returns.
    """

    # Reopenthe working file
    working_file = open(working_file_name, "a")


    working_file.write("\n")
    working_file.write("---------------------------------------------------------\n")
    working_file.write("generate_overlayfs_stacking\n")
    working_file.write("---------------------------------------------------------\n")
    working_file.write("\n")



    # Reopen the working file
    working_file = open(working_file_name, "a")

    # Check that the stack definition is in the configuration file
    if "stack_definition" not in self.project.firmware_definition["layout"]:
      self.project.logging.critical("The stack definition is not in the configuration file")
      exit(1)

    # Iterates the stack items
    for item in self.project.firmware_definition["layout"]["stack_definition"]:
      # Generate the mount point creation code
      working_file.write("# Stack the   " + item["stack_item"]["type"] +
                         " '" + item["stack_item"]["name"] + "'\n")

      # Generate the tmpfs specific mount command
      if item["stack_item"]["type"] == "tmpfs":
        working_file.write("mount -t overlay overlay -olowerdir=")
        working_file.write(item["stack_item"]["mountpoint"] + ",upperdir=/mnt/dft/")
        working_file.write(item["stack_item"]["name"] + "/mountpoint")
        working_file.write(",workdir=/mnt/dft/" + item["stack_item"]["name"] + "/workdir\n")
        working_file.write(" " + item["stack_item"]["mountpoint"] + "\n")

      # Generate the tmpfs specific mount command
      if item["stack_item"]["type"] == "squashfs":
        working_file.write("mount -t overlay overlay -olowerdir=/mnt/dft/")
        working_file.write(item["stack_item"]["name"] + ":" + item["stack_item"]["mountpoint"])
        working_file.write(" " + item["stack_item"]["mountpoint"] + "\n")

      # Generate the tmpfs specific mount command
      if item["stack_item"]["type"] == "partition":
        working_file.write("mount -t overlay overlay -olowerdir=")
        working_file.write(item["stack_item"]["mountpoint"] + ",upperdir=/mnt/dft/")
        working_file.write(item["stack_item"]["name"])
        working_file.write(",workdir=/mnt/dft/workdir\n")
        working_file.write(" " + item["stack_item"]["mountpoint"] + "\n")

      working_file.write("\n")

    # We are done here, now close the file
    working_file.close()



  # -------------------------------------------------------------------------
  #
  # generate_aufs_stacking
  #
  # -------------------------------------------------------------------------
  def generate_aufs_stacking(self, working_file_name):
    """This method generates the command needed tostack the file systems
    using aufs.

    It takes as argument the output file opened by the calling method. This
    method only do output, the file is closed after the method returns.
    """

    # Reopenthe working file
    working_file = open(working_file_name, "a")

    working_file.write("generate_aufs_stacking\n")
# sudo mount -t aufs -o noatime,nodiratime,br:${systemdir}=rr -o udba=reval none ${mountdir}

    # We are done here, now close the file
    working_file.close()
