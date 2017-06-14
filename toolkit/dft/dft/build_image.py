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
    """XXXX This method installs in the generated rootfs the tools needed to update
    (or generate) theinitramfs. The kernel is not installed, it is the job of
    the install_bootchain target. The kernel to use is defined in the BSP
    used by this target.

    Operations executed by this method run in a chrooted environment in the
    generated rootfs.
    """

    # Output current task to logs
    logging.info("Creating the target image file")

  # -------------------------------------------------------------------------
  #
  # setup_loopback
  #
  # -------------------------------------------------------------------------
  def setup_loopback(self):
    """XXXX This method installs in the generated rootfs the tools needed to update
    (or generate) theinitramfs. The kernel is not installed, it is the job of
    the install_bootchain target. The kernel to use is defined in the BSP
    used by this target.

    Operations executed by this method run in a chrooted environment in the
    generated rootfs.
    """

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
    """XXXX This method installs in the generated rootfs the tools needed to update
    (or generate) theinitramfs. The kernel is not installed, it is the job of
    the install_bootchain target. The kernel to use is defined in the BSP
    used by this target.

    Operations executed by this method run in a chrooted environment in the
    generated rootfs.
    """

    # Output current task to logs
    logging.info("Umounting the image and releasing the loopback devices")
