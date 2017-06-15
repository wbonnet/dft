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

""" This module provides functionnalities used to create a binary image of a media from
the rootfs and bootchain.
"""

import logging
import os
from cli_command import CliCommand
from model import Key

#
#    Class BuildImage
#
class BuildImage(CliCommand):
  """This class implements method needed to build the image which will be
  written in flash memory or on a SD card.
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

    # Defines the loopback device used for image building. Initialiy it is None
    # Its value is retrieved from a call to "losetup -f" and stored in this member
    # Once released the member is set back to None
    self.loopback_device = None

    # Defines the absolute filepath to the image file. Default value is none. Value
    # is set when configuration is checked, and never set back to None.
    self.image_path = None

    # Flag used to know if the image is mounted or not. Initial value is False
    self.image_is_mounted = False



  # -------------------------------------------------------------------------
  #
  # build_image
  #
  # -------------------------------------------------------------------------
  def build_image(self):
    """This method implement the business logic of image generation. Image
    is a file containing the dump of what will be copied on the target
    storage device (harddisk or flash for example). It calls dedicated
    method for each step. The main steps are :

    . Creating the empty image file
    . Setup the loopback device
    . Copy rootfs content to image
    . Install the boot sectors
    . Umount the image and release loopback
    """

    # Create the image file
    self.create_image()

    # Create the loopbck device and mount the image file
    self.setup_loopback()

    # Setup the partitions in the image
    self.create_partitions()

    # Copy rootfs to the image
    self.install_image_content()

    # Install the boot (either grub or uboot)
    self.install_boot()

    # Umount the image and release the loopback deice
    self.umount_image()



  # -------------------------------------------------------------------------
  #
  # create_image
  #
  # -------------------------------------------------------------------------
  def create_image(self):
    """This method is in charge of crating the empty image file. The image
    file will later be mounted as a loop device, receive partitions, boot and
    rootfs content.

    The image is defined by the following parameters:
    . Filename of the image
    . Image size
    . Fill method (used to create initial content
    """

    # Check that there is an image configuration file first
    if self.project.image is None:
      self.project.logging.critical("The image configuration file is not defined in project file")
      exit(1)

    # Check that the devices is available from the configuration file
    if Key.DEVICES.value not in self.project.image:
      self.project.logging.critical("The image devices is not defined in configuration file")
      exit(1)

    # Check that the filename is available from the devices section in the configuration file
    if Key.FILENAME.value not in self.project.image[Key.DEVICES.value]:
      self.project.logging.critical("The filename is not defined in the configuration file")
      exit(1)

    # Continue to check everything needed is defined
    if Key.SIZE.value not in self.project.image[Key.DEVICES.value]:
      self.project.logging.critical("Image size is not defined in the devices section. Aborting.")
      exit(1)
    else:
      try:
        size = int(self.project.image[Key.DEVICES.value][Key.SIZE.value])
      except ValueError:
        self.project.logging.critical("Image size is not a number : " +
                                      self.project.image[Key.DEVICES.value][Key.SIZE.value])
        exit(1)

    # Continue to check everything needed is defined
    if Key.UNIT.value not in self.project.image[Key.DEVICES.value]:
      self.project.logging.warning("Image size unit is not defined, defaultig to MB.")
      unit = "MB"
    else:
      unit = self.project.image[Key.DEVICES.value][Key.UNIT.value].lower()

    # Compute the block size to use based on the unit
    if unit == "s": block_size = 512
    elif unit == "b": block_size = 1
    elif unit == "kb" or unit == "kib": block_size = 1024
    elif unit == "mb" or unit == "mib": block_size = 1024 * 1024
    elif unit == "gb" or unit == "gib": block_size = 1024 * 1024 * 1024
    elif unit == "tb" or unit == "tib": block_size = 1024 * 1024 * 1024 * 1024
    else:
      self.project.logging.critical("Unknwon unit '" + unit + "' . Aborting")
      exit(1)

    # Some logging :)
    self.project.logging.debug("Image size unit is '" + str(unit) + "', block size is " + str(block_size))

    if Key.FILL_METHOD.value not in self.project.image[Key.DEVICES.value]:
      self.project.logging.warning("Image fill method is not defined, defaultig to (filled with) zero.")
      fill_method = "zero"
    else:
      fill_method = self.project.image[Key.DEVICES.value][Key.FILL_METHOD.value]

    if fill_method != "zero" and fill_method != "random":
      self.project.logging.critical("Unknown fill method '" + fill_method + "' . Aborting")
      exit(1)

    # Some logging :)
    self.project.logging.debug("Image fill method is '" + fill_method + "'")

    # Ensure target rootfs mountpoint exists and is a dir
    if os.path.isfile(self.project.get_image_directory()):
      self.project.logging.critical("Image target directory aldredy exist but is a file !")
      exit(1)

    # Create the directory if needed
    if not os.path.isdir(self.project.get_image_directory()):
      os.makedirs(self.project.get_image_directory())

    # Generate the path
    self.image_path = self.project.get_image_directory() + "/"
    self.image_path += self.project.image[Key.DEVICES.value][Key.FILENAME.value]
    self.project.logging.debug("The image file is : " + self.image_path)

    # Check if the image already exist and is a dir
    if os.path.isdir(self.image_path):
      self.project.logging.critical("Image target file aldredy exist but is a directory !")
      exit(1)

    # Check if the image already exist
    if os.path.isfile(self.image_path):
      self.project.logging.debug("Image target aldredy exist, removing it")
      os.remove(self.image_path)

# utilise dd
# retrouver les parametres
# size
# unit
# fill_method

#     supprimer le fichier s'il existe ?
    sudo_command = "touch " + self.image_path
#    sudo_command_output = self.execute_command(sudo_command)
    print(sudo_command)

    # Output current task to logs
    logging.info("Creating the target image file")

    exit(0)

  # -------------------------------------------------------------------------
  #
  # setup_loopback
  #
  # -------------------------------------------------------------------------
  def setup_loopback(self):
    """This method is in charge of setting up the loopback device using the
    image created.

    There is two main step :
    . Find the next available loopback device
    . Mout the file in the loopbck device
    """

    # Retrieve the next available loopback device
    sudo_command = "sudo /sbin/losetup -f"
    sudo_command_output = self.execute_command(sudo_command)

    # Parse the output to retrive the device and store it
    binaryline = sudo_command_output.splitlines()
    self.loopback_device = binaryline[0].decode(Key.UTF8.value)

    # Check that the image is not mounted and path is defined and exist
    if not self.image_is_mounted:
      if self.image_path is not None:
        if os.path.isfile(self.image_path):
          # Mount the image in the loopback device
          sudo_command = "sudo /sbin/losetup " + self.loopback_device + " " + self.image_path
          sudo_command_output = self.execute_command(sudo_command)
          # Set the flag to True, if an error occured an exception has been raised, and this line
          # is not executed
          self.image_is_mounted = True
        else:
          logging.critical("Image file " + self.image_path + " does not exist. Aborting !")
          exit(1)
      else:
        logging.critical("Image file path is not defined. Aborting !")
        exit(1)
    else:
      logging.critical("Image is already mounted. Aborting !")
      exit(1)

    # Output current task to logs
    logging.info("Setting up the loopback device")



  # -------------------------------------------------------------------------
  #
  # create_partitions
  #
  # -------------------------------------------------------------------------
  def create_partitions(self):
    """XXXX This method installs in the generated rootfs the tools needed to update
    (or generate) theinitramfs. The kernel is not installed, it is the job of
    the install_bootchain target. The kernel to use is defined in the BSP
    used by this target.

    Operations executed by this method run in a chrooted environment in the
    generated rootfs.
    """

    # Output current task to logs
    logging.info("Creating the partitions in the image mounted in loopback")



  # -------------------------------------------------------------------------
  #
  # install_image_content
  #
  # -------------------------------------------------------------------------
  def install_image_content(self):
    """XXXX This method installs in the generated rootfs the tools needed to update
    (or generate) theinitramfs. The kernel is not installed, it is the job of
    the install_bootchain target. The kernel to use is defined in the BSP
    used by this target.

    Operations executed by this method run in a chrooted environment in the
    generated rootfs.
    """

    # Output current task to logs
    logging.info("Installating image content")



  # -------------------------------------------------------------------------
  #
  # install_boot
  #
  # -------------------------------------------------------------------------
  def install_boot(self):
    """XXXX This method installs in the generated rootfs the tools needed to update
    (or generate) theinitramfs. The kernel is not installed, it is the job of
    the install_bootchain target. The kernel to use is defined in the BSP
    used by this target.

    Operations executed by this method run in a chrooted environment in the
    generated rootfs.
    """

    # Output current task to logs
    logging.info("Installating the boot (uboot or grub)")



  # -------------------------------------------------------------------------
  #
  # umount_image
  #
  # -------------------------------------------------------------------------
  def umount_image(self):
    """This method is in charge of cleaning the environment once image content
    is written.

    The main steps are :
    . umounting the image
    . release the loopback device
    """

    # Check that the loopback device is defined
    if self.loopback_device is not None:
      # Copy the stacking script to /tmp in the rootfs
      sudo_command = 'sudo losetup -d ' + self.loopback_device
      self.execute_command(sudo_command)

      # Loopback has been released, set the member to None
      self.loopback_device = None

      # Image has been umounted, set the member flag to None
      self.image_is_mounted = False
    else:
      logging.debug("Loopback device is not defined")

    # Output current task to logs
    logging.info("Umounting the image and releasing the loopback devices")
