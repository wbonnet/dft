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
import parted
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

    # Create and format the filesystems on the newly created partitions
    self.create_filesystems()

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

    # Output current task to logs
    logging.info("Creating the target image file")

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
      unit = "mb"
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
    self.project.logging.debug("Image size unit is '" + str(unit) + "', block size is " +
                               str(block_size))

    if Key.FILL_METHOD.value not in self.project.image[Key.DEVICES.value]:
      self.project.logging.warning("Image fill method is not defined, filling with zero.")
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

    # Create the fill command
    sudo_command = "dd if=/dev/" + fill_method + " of=" + self.image_path
    sudo_command += " bs=" + str(block_size) + " count=" + str(size)
    sudo_command_output = self.execute_command(sudo_command)



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
    """This method creates the partition table and the different partitions
    in the loopback device. It first read the device definition, then iterate
    the list of partitions.

    Device operation are done using the pyparted library.
    """
#TODO cleanup method to remove loopback

    # Output current task to logs
    logging.info("Creating the partitions in the image mounted in loopback")

    # Retrieve the partition type to create
    if Key.LABEL.value not in self.project.image[Key.DEVICES.value]:
      self.project.logging.warning("Partition table label is not defined, defaulting to dos.")
      label = "msdos"
    else:
      label = self.project.image[Key.DEVICES.value][Key.LABEL.value]

    # Check that the value is in the list of valid values
    if label not in "aix" "amiga" "bsd" "dvh" "gpt" "loop" "mac" "msdos" "pc98" "sun":
      self.project.logging.critical("Unknown partition label '" + label + "' . Aborting")
      exit(1)
    else:
      self.project.logging.debug("Using partition label '" + label + "'")

    # Retrieve the partition alignment
    if Key.ALIGNMENT.value not in self.project.image[Key.DEVICES.value]:
      self.project.logging.warning("Partition alignment is not defined, defaulting to none.")
      alignment = "none"
    else:
      alignment = self.project.image[Key.DEVICES.value][Key.ALIGNMENT.value]

    # TODO : handle partition alignment

    # Check that the value is in the list of valid values
    # if alignment == "none":
    #   parted_alignment = None
    # elif alignment == "optimal":
    #   parted_alignment = parted.OPTIMAL
    # elif alignment == "cylinder":
    #   parted_alignment = cylinder
    # elif alignment == "minimal":
    #   parted_alignment = minimal
    # else:
    #   self.project.logging.critical("Unknown partition alignment '" + alignment + "' . Aborting")
    #   exit(1)

    self.project.logging.debug("Using partition alignment '" + alignment + "'")

    # Create the partition tabl on the device
    device = parted.getDevice(self.loopback_device)

    # Create a new disk object
    disk = parted.freshDisk(device, label)

    # Check that there is a partition table inthe configuration file. If not it will fail later,
    # thus better fail now.
    if Key.PARTITIONS.value not in self.project.image[Key.DEVICES.value]:
      self.project.logging.error("Partition table is not defined, nothing to do. Aborting")
      exit(1)

    # Nox iterate the partitiontables and create them
    for partition in self.project.image[Key.DEVICES.value][Key.PARTITIONS.value]:

      # Retrieve the partition name
      if Key.NAME.value in partition:
        part_name = partition[Key.NAME.value]
      else:
        part_name = ""

      self.project.logging.debug("Partition name =>  '" + part_name + "'")

      # Retrieve the partition type
      if Key.TYPE.value in partition:
        part_type = partition[Key.TYPE.value]
      else:
        part_type = "primary"

      # Check that the partition type is valid and convert in parted "define"
      if part_type == "primary":
        parted_type = parted.PARTITION_NORMAL
      elif part_type == "extended":
        parted_type = parted.PARTITION_EXTENDED
      elif part_type == "logical":
        parted_type = parted.PARTITION_LOGICAL
      else:
        self.project.logging.critical("Unknown partition type '" + part_type + "' . Aborting")
        exit(1)

      self.project.logging.debug("Partition type =>  '" + part_type + "'")

      # Retrieve the partition size
      if Key.SIZE.value not in partition:
        self.project.logging.critical("Partition size is not defined. Aborting")
        exit(1)
      else:
        # Retrieve the value and control it is an integer
        try:
          part_size = int(partition[Key.SIZE.value])
        except ValueError:
          self.project.logging.critical("Partition size is not a number : " +
                                        partition[Key.SIZE.value])
          exit(1)

      self.project.logging.debug("Partition size => '" + str(part_size) + "'")

      # Retrieve the partition unit
      if Key.UNIT.value not in partition:
        self.project.logging.warning("Partition size unit is not defined, defaultig to MB.")
        part_unit = "MB"
      else:
        part_unit = partition[Key.UNIT.value]

      # Compute the block size to use based on the unit
      if part_unit not in "s" "B" "KB" "KiB" "MB" "MiB" "GB" "GiB" "TB" "TiB":
        self.project.logging.critical("Unknwon unit '" + part_unit + "' . Aborting")
        exit(1)
      else:
        self.project.logging.debug("Partition unit => '" + part_unit + "'")

      # Retrieve the partition start sector
      if Key.START_SECTOR.value not in partition:
        self.project.logging.warning("Partition start_sector is not defined. " +
                                     "Using next available in sequence")
        part_start_sector = -1
      else:
        # Retrieve the value and control it is an integer
        try:
          part_start_sector = int(partition[Key.START_SECTOR.value])
        except ValueError:
          self.project.logging.critical("Partition start_sector is not a number : " +
                                        partition[Key.START_SECTOR.value])
          exit(1)

      self.project.logging.debug("Partition start sector => '" + str(part_start_sector) + "'")

      # Retrieve the partition flags
      if Key.FLAGS.value not in partition:
        self.project.logging.debug("Partition flags are not defined. Skipping...")
        part_flags = None
      else:
        part_flags = partition[Key.FLAGS.value]
        self.project.logging.debug("Partition flags => '" + part_flags + "'")

      # Retrieve the partition file system type
      if Key.FILESYSTEM.value not in partition:
        self.project.logging.debug("File system to create on the partition is not defined.")
        part_filesystem = None
      else:
        part_filesystem = partition[Key.FILESYSTEM.value].lower()
        # Check that the value is in the list of valid values
        if part_filesystem not in  parted.fileSystemType:
          self.project.logging.critical("Unknown filesystem type '" + part_filesystem +
                                        "' . Aborting")
          exit(1)
        else:
          self.project.logging.debug("Filesystem type =>  '" + part_filesystem + "'")

      # Retrieve the partition format flag
      if Key.FORMAT.value not in partition:
        self.project.logging.debug("File system format flag is not defined. Defaulting to True")
        part_format = True
      else:
        part_format = partition[Key.FORMAT.value]
        self.project.logging.debug("File system format flag => '" + str(part_format) + "'")

      #
      # All information have been parsed,now let's create the partition in the loopback device
      #

      # Compute the sector count based on size and unit. Need for parted
      sector_count = parted.sizeToSectors(part_size, part_unit, device.sectorSize)

      # Compute the geometry for this device
      geometry = parted.Geometry(start=part_start_sector, length=sector_count, device=device)

      # Create the arted filesystem object
      fs = parted.FileSystem(type=part_filesystem, geometry=geometry)

      # Create the partition object in the loopback device
      new_partition = parted.Partition(disk=disk, type=parted_type, geometry=geometry, fs=fs)

      # Create the constraint object for alignment, etc.
      # constraint = parted.Constraint(startAlign=parted_alignment, endAlign=parted_alignment, \
      #              startRange=start, endRange=end, minSize=min_size, maxSize=max_size)
      constraint = parted.Constraint(exactGeom=new_partition.geometry)

      # Add the partition to the disk
      disk.addPartition(partition=new_partition, constraint=constraint)

    # Make modification persistent to disk
    disk.commit()



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

  # -------------------------------------------------------------------------
  #
  # create_filesystes
  #
  # -------------------------------------------------------------------------
  def create_filesystems(self):
    """This method creates the file systems on the partition created by the
    create_partitions method. It uses the same configuration file.

    File system creation is implemented in a different method since it has tp
    be done after partition creation and commit. It can't be done on the fly.

    This code has been separated to make it more easy to read and maintain.

    Since it is executed in sequence after partition creation, configuration
    file is not checked again for the same parameters. Only parameters
    specific to filesystems are checked.
    """

    # Output current task to logs
    logging.info("Creating the filesystems in the newly created partitions")

    # Defines a partition counter. Starts at zerp and is incremented at each iteration
    # beginning. It means first partition is 1.
    part_index = 0

    # Nox iterate the partitiontables and create them
    for partition in self.project.image[Key.DEVICES.value][Key.PARTITIONS.value]:

      # Increase partition index
      part_index += 1

      # Retrieve the partition format flag
      if Key.FORMAT.value not in partition:
        self.project.logging.debug("File system format flag is not defined. Defaulting to True")
        part_format = True
      else:
        part_format = partition[Key.FORMAT.value]
        self.project.logging.debug("File system format flag => '" + str(part_format) + "'")

      # Check if the flag is true, if not there is nothing to do
      if not part_format:
        self.project.logging.debug("The format flag is deactivated for martition " + part_index)
      else:
        # Retrieve the partition file system type
        if Key.FILESYSTEM.value not in partition:
          self.project.logging.debug("File system to create on the partition is not defined.")
          part_filesystem = None
        else:
          part_filesystem = partition[Key.FILESYSTEM.value].lower()

        # Default is having no format nor tunefs tool. It will be checked after fs type
        # control and tool command guessing
        format_tool = None
        tune_tool = None

        # Check that the value is in the list of valid values
        if part_filesystem == "ext2":
          format_tool = "mkfs.ext2"
          tune_tool = "tune2fs"
        elif part_filesystem == "ext3":
          format_tool = "mkfs.ext3"
          tune_tool = "tune2fs"
        elif part_filesystem == "ext4":
          format_tool = "mkfs.ext4"
          tune_tool = "tune2fs"
        elif part_filesystem == "fat32":
          format_tool = "mkfs.vfat"
        elif part_filesystem == "linux-swap(v0)" or part_filesystem == "linux-swap(v1)":
          format_tool = "mkswap"

        # Creation du file fystem sur a prtition
        sudo_command = 'sudo ' + format_tool + ' ' + self.loopback_device + 'p' + str(part_index)
        self.execute_command(sudo_command)

      # Retrieve the reserved size
      if Key.RESERVED_SIZE.value not in partition:
        self.project.logging.debug("Partition reserved size is not defined, skipping tune2fs.")
      # else:
        # Copy the stacking script to /tmp in the rootfs
        # sudo_command = 'sudo ' + tune_tool + ' ' +
        # + self.device + 'p' + part_index
        # # self.execute_command(sudo_command)
        # print(sudo_command)

#faire le tune2fs
#mettre le parametre dans image
#voir le man si yen a d'autre
#penser a faire des fsck apres la copie
#faire un tableau des fs ? genre dans partoche
#restera a trouver comment ordonner les points de montage


