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
import stat
import tempfile
import datetime
import glob
from dft.cli_command import CliCommand
from dft.enumkey import Key


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

    # Defines dft base directory in the initramfs file system.
    # Should always be /dft
    self.dft_root = "/dft"

    # Defines stack mount point in the iniarmfs file system.
    # Should alwaays be /root
    self.stack_root = "/root"

  # -------------------------------------------------------------------------
  #
  # assemble_firmware
  #
  # -------------------------------------------------------------------------
  def assemble_firmware(self):
    """This method implement the business logic of firmware assembling.

    Assembling a firmware, use as input the firmware file created from a
    rootfs and then generate the configuration files used to loading after
    booting. The configuration is used to define how the filesystems are
    stacked, what should be the physical partitionning, ciphering, etc.

    It calls dedicated method for each step. The main steps are :
    .
    """

    # Check that there is a firmware configuration file first
    if self.project.firmware is None:
      self.project.logging.critical("The firmware configuration file is not defined in \
                                     project file")
      exit(1)

    # Check that the layout is available from the firmware configuration file
    if Key.LAYOUT.value not in self.project.firmware:
      self.project.logging.critical("The firmware layout is not defined in configuration file")
      exit(1)

    # Check that the stacking method is available from the firmware configuration file
    if Key.METHOD.value not in self.project.firmware[Key.LAYOUT.value]:
      self.project.logging.critical("The firmware stacking method is not defined")
      exit(1)

    # Ensure firmware generation path exists and is a dir
    os.makedirs(self.project.get_firmware_content_directory(), exist_ok=True)

    # Ensure firmware exists
    if not os.path.isfile(self.project.firmware_filename):
      logging.critical("The firmware does not exist (" + self.project.firmware_filename + ")")
      exit(1)

    # Remove existing initscript if needed
    if os.path.isfile(self.project.init_filename):
      os.remove(self.project.init_filename)

    # Check if we are working with foreign arch
    if self.use_qemu_static:
      # QEMU is used, and we have to install it into the target
      self.setup_qemu()

    # Generate the stacking script
    self.generate_stacking_script()

    # Install the packages and tools needed to create the updated bootchain
    self.install_initramfs_tools()

    # Customize the content of the initramfs
    self.customize_initramfs_modules()
    self.customize_initramfs_binaries()

    # Regenerate the initramfs to include our custum stacking script and some modification
    # to the init script ( needed to call the stacking script )
    self.update_initramfs()

    # Remove QEMU if it has been isntalled. It has to be done in the end
    # since some cleanup tasks could need QEMU
    if self.use_qemu_static:
      self.cleanup_qemu()

    # Copy the new / updated bootchain from the rootfs to the output directory
    self.copy_bootchain_to_output()



  # -------------------------------------------------------------------------
  #
  # install_initramfs_tools
  #
  # -------------------------------------------------------------------------
  def install_initramfs_tools(self):
    """This method installs in the generated rootfs the tools needed to update
    (or generate) theinitramfs. The kernel is not installed, it is the job of
    the install_bootchain target. The kernel to use is defined in the BSP
    used by this target.

    Operations executed by this method run in a chrooted environment in the
    generated rootfs.
    """

    # Output current task to logs
    logging.info("Installing initramfs tools and kernel")

    # Install initramfs-tools to the rootfs
    self.install_package("initramfs-tools")



  # -------------------------------------------------------------------------
  #
  # update_initramfs
  #
  # -------------------------------------------------------------------------
  def update_initramfs(self):
    """This method regerenate (or create if missing) the initramfs. This
    operation is ran from the chrooted environment. Stacking script and
    modifications to the init script are included during this stage.
    """

    # Output current task to logs
    self.project.logging.info("Updating initramfs")

    # Copy the stacking script to /tmp in the rootfs
    command = "LANG=C chroot " + self.project.get_rootfs_mountpoint()
    command += " update-initramfs -t -u -k all"
    self.execute_command(command)

    # Check if we have to run mkimage to make it bootable on ARM or PowerPC
    # boards
    if Key.MKIMAGE.value in self.project.firmware[Key.INITRAMFS.value] and \
       self.project.firmware[Key.INITRAMFS.value][Key.MKIMAGE.value]:
      # Retrieve compression from configuration file
      if Key.MKIMAGE_COMPRESSION.value in self.project.firmware[Key.INITRAMFS.value]:
        if self.project.firmware[Key.INITRAMFS.value][Key.MKIMAGE_COMPRESSION.value] not in \
                "gzip" "bzip2" "lz4" "lzma" "lzo" "none":
          self.project.logging.error("Unknown mkimage compression method : " + \
                   self.project.firmware[Key.INITRAMFS.value][Key.MKIMAGE_COMPRESSION.value])
          self.project.logging.error("Using gzip instead")
          mkimage_compression = Key.GZIP.value
        else:
          mkimage_compression = self.project.firmware[Key.INITRAMFS.value]\
                                                     [Key.MKIMAGE_COMPRESSION.value]
      else:
        mkimage_compression = Key.GZIP.value

      # Retrieve architecture from configuration file
      if Key.MKIMAGE_ARCH.value in self.project.firmware[Key.INITRAMFS.value]:
        if self.project.firmware[Key.INITRAMFS.value][Key.MKIMAGE_ARCH.value] not in \
           "alpha" "arc" "arm" "arm64" "avr32" "blackfin" "ia64" "invalid" "m68k" "microblaze" \
           "mips" "mips64" "nds32" "nios2" "or1k" "powerpc" "s390" "sandbox" "sh" "sparc" \
           "sparc64" "x86" "x86_64" "xtensa":
          self.project.logging.error("Unknown mkimage architecture : " + \
                   self.project.firmware[Key.INITRAMFS.value][Key.MKIMAGE_ARCH.value])
          self.project.logging.error("Using invalid instead")
          mkimage_arch = Key.INVALID.value
        else:
          mkimage_arch = self.project.firmware[Key.INITRAMFS.value][Key.MKIMAGE_ARCH.value]
      else:
        mkimage_arch = self.project.get_mkimage_arch()

      # Iterate all the initrd generated under /boot in the chroot directory
      filepath = self.project.get_rootfs_mountpoint() + '/boot/initrd.img-*'
      for initrdfile in glob.glob(filepath):
        # Rename the file
        os.rename(initrdfile, initrdfile + ".old")

        # Generate the mkimage command
        self.project.logging.debug("Running mkimage on initramfs")
        command = "mkimage -A " + mkimage_arch + " -T ramdisk -C " + mkimage_compression
        command += " -d " + initrdfile + ".old " + initrdfile
        self.execute_command(command)

        # Remove the old initrd file
        os.remove(initrdfile + ".old")
    else:
      self.project.logging.debug("Running mkimage on initrd is deactivated in configuration file")


  # -------------------------------------------------------------------------
  #
  # copy_bootchain_to_output
  #
  # -------------------------------------------------------------------------
  def copy_bootchain_to_output(self):
    """This method copy the bootchain that has been installed / updated from the
    generated rootfs to the output directory on the host.
    """

    # Output current task to logs
    self.project.logging.info("Copying bootchain to firmware directory")

    # Create boot  under firmware directory
    os.makedirs(self.project.get_firmware_content_directory() + "/boot", exist_ok=True)

    # Copy the stacking script to /tmp in the rootfs
    source_dir = self.project.get_rootfs_mountpoint() + '/boot/'
    command = "cp -fra " + source_dir + " " + self.project.get_firmware_content_directory()
    self.execute_command(command)

    # for copy_target in os.listdir(source_dir):
    #   copy_source_path = os.path.join(source_dir, copy_target)
    #   copy_target_path = os.path.join(self.project.get_firmware_content_directory(), copy_target)
    #   copy_target_path = self.project.get_firmware_content_directory() + "/"
    #   command = "cp -fra " + copy_source_path + " " + copy_target_path
    #   self.execute_command(command)



  # -------------------------------------------------------------------------
  #
  # customize_initramfs_modules
  #
  # -------------------------------------------------------------------------
  def customize_initramfs_modules(self):
    """This method customize the list of modules loaded in the initramfs, and
    copy the stacking scipt to the scipt directory, so it will be included in
    the initramfs once generated.
    """

    # Output current task to logs
    self.project.logging.info("Customize modules list in target")

    # Create a file in modules.d to ensure that squashfs and overlay modules are present
    # Also install any modules needed by the firmware to stack the file systems (overlay or aufs)
    # or declared in the configuration file as additional
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as working_file:
      # Squashfs is mandatory
      # Detect if it is used or not
      working_file.write("squashfs\n")

      # Check if aufs or ovelayfs are needed
      if self.project.firmware[Key.LAYOUT.value][Key.METHOD.value] == Key.AUFS.value:
        working_file.write("aufs\n")
      elif self.project.firmware[Key.LAYOUT.value][Key.METHOD.value] == Key.OVERLAYFS.value:
        working_file.write("overlay\n")
      else:
        # If we reach this code, then method was unknown
        self.project.logging.error("Unknown stacking method " +
                                   self.project.firmware[Key.LAYOUT.value][Key.METHOD.value])

      # Check if there is an initramfs customization section
      if Key.INITRAMFS.value in self.project.firmware:
        # Yes, so now look for an additional module section
        if Key.ADDITIONAL_MODULES.value in self.project.firmware[Key.INITRAMFS.value]:
          # Generate an entry for additional each module to load in initramfs as defined in
          # the configuration file
          for module in self.project.firmware[Key.INITRAMFS.value][Key.ADDITIONAL_MODULES.value]:
            working_file.write(module + "\n")
            logging.debug("adding additional module : " + module + " to initramfs")
        else:
          logging.debug("initramfs section found, but no additional module to include are defined")
      else:
        logging.debug("no initramfs section found")

    # Done close the file
    working_file.close()

    # And now we can move the temporary file under the rootfs tree
    filepath = self.project.get_rootfs_mountpoint() + '/usr/share/initramfs-tools/modules.d/'
    command = "mv -f " + working_file.name + " " + filepath + "extra-modules"
    self.execute_command(command)



  # -------------------------------------------------------------------------
  #
  # customize_initramfs_binaries
  #
  # -------------------------------------------------------------------------
  def customize_initramfs_binaries(self):
    """This method customize the list of binaires included in the initramfs.
    It is done by adding a hook script doing the copy_exec call when
    updateinitramfs runs.
    """

    # Output current task to logs
    logging.info("Customize binaries list in target")

    # Create a file in hooks to ensure that some mandatory binary commands are present
    # Also install any modules needed by the firmware to stack the file systems (overlay or aufs)
    # or declared in the configuration file as additional
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as working_file:
      working_file.write("#/bin/sh -e\n")
      working_file.write("\n")
      working_file.write("\n")
      working_file.write("\n")
      working_file.write("#\n")
      working_file.write("# Copy necessary binaries to initramfs\n")
      working_file.write("#\n")
      working_file.write("# This script has been generated automatically by the DFT toolkit.\n")
      working_file.write("# It is in charge of copying the needed binaries into initramfs\n")
      working_file.write("# while it is updated.\n")
      working_file.write("\n")
      working_file.write("PREREQ=""\n")
      working_file.write("prereqs()\n")
      working_file.write("{\n")
      working_file.write("    echo \"$PREREQ\"\n")
      working_file.write("}\n")
      working_file.write("\n")
      working_file.write("case $1 in\n")
      working_file.write("prereqs)\n")
      working_file.write("    prereqs\n")
      working_file.write("    exit 0\n")
      working_file.write("    ;;\n")
      working_file.write("esac\n")
      working_file.write("\n")
      working_file.write("\n")
      working_file.write("\n")
      working_file.write(". /usr/share/initramfs-tools/hook-functions\n")
      working_file.write("\n")
      # Ensure that loopback device is enabled
      working_file.write("# ----- Copy the binaries using copy_exec -----\n")
      working_file.write("copy_exec /sbin/fsck.ext4 /sbin\n")
      working_file.write("copy_exec /sbin/e2fsck    /sbin\n")

      # Check if there is an initramfs customization section
      if Key.INITRAMFS.value in self.project.firmware:
        # Yes, so now look for an additional module section
        if Key.ADDITIONAL_BINARIES.value in self.project.firmware[Key.INITRAMFS.value]:
          # Generate an entry for additional each module to load in initramfs as defined in
          # the configuration file
          for binary in self.project.firmware[Key.INITRAMFS.value][Key.ADDITIONAL_BINARIES.value]:
            working_file.write("copy_exec /usr/bin/" + binary + " /bin\n")
            logging.debug("adding additional binary : " + binary + " to initramfs")
        else:
          logging.debug("initramfs section found, but no additional binary to include are defined")
      else:
        logging.debug("no initramfs section found")

    # Done close the file
    working_file.close()

    # Update stack script permissions. It has to be executable and world readable (not reuiered
    # but easier to handle)
    os.chmod(working_file.name, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | \
             stat.S_IROTH | stat.S_IXOTH)

    # And now we can move the temporary file under the rootfs tree
    filepath = self.project.get_rootfs_mountpoint() + '/usr/share/initramfs-tools/hooks/'
    command = "mv -f " + working_file.name + " " + filepath + "extra-binaries"
    self.execute_command(command)



  # -------------------------------------------------------------------------
  #
  # generate_stacking_script
  #
  # -------------------------------------------------------------------------
  def generate_stacking_script(self):
    """This method implement the generation of the stacking script

    The stacking script is called in the initramfs by the init script. Stacking
    script is a shell scipt generated using the firmware.yml configuration
    as input. It provides th specific cod used to mount and stack the filesystms
    (using aufs or overlayfs).
    """

    # Retrieve generation date
    today = datetime.datetime.now()

    # Output current task to logs
    logging.info("Generating stacking scripts")

    # Generate the stacking script
    # configuration, then move  roles to the target rootfs
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as working_file:

      # Generate file header
      working_file.write("#/bin/sh -e\n")
      working_file.write("\n")
      working_file.write("# This script has been generated automatically by the DFT toolkit.\n")
      working_file.write("# It is in charge of mounting and stacking the different items\n")
      working_file.write("# of the firmware.\n")
      working_file.write("\n")
      working_file.write("#\n")
      working_file.write("# Generation date : " + today.strftime("%d/%m/%Y - %H:%M.%S") + "\n")
      working_file.write("#\n")
      working_file.write("\n")
      working_file.write("PREREQ=""\n")
      working_file.write("prereqs()\n")
      working_file.write("{\n")
      working_file.write("    echo \"$PREREQ\"\n")
      working_file.write("}\n")
      working_file.write("\n")
      working_file.write("case $1 in\n")
      working_file.write("prereqs)\n")
      working_file.write("    prereqs\n")
      working_file.write("    exit 0\n")
      working_file.write("    ;;\n")
      working_file.write("esac\n")
      working_file.write("\n")
      working_file.write("\n")
      working_file.write("\n")
      working_file.write("# ---------------------------------------------------------\n")
      working_file.write("# Setup DFT environment\n")
      working_file.write("# ----------------------------------------------------------\n")
      working_file.write("\n")

      # Ensure that loopback device is enabled
      working_file.write("# ----- Ensure that the meeded modules are loaded -----\n")
      working_file.write("modprobe loop\n")

      if self.project.firmware[Key.LAYOUT.value][Key.METHOD.value] == Key.AUFS.value:
        working_file.write("modprobe aufs\n")
      elif self.project.firmware[Key.LAYOUT.value][Key.METHOD.value] == Key.OVERLAYFS.value:
        working_file.write("modprobe overlay\n")

      working_file.write("\n")

    # Now it's done, let's close the file
    working_file.close()

    # Generate the common stuff. It includes mounting the target (used later for stacking them)
    self.generate_common_mount(working_file.name)

    # Call the method dedicated to the selected stacking method
    if self.project.firmware[Key.LAYOUT.value][Key.METHOD.value] == Key.AUFS.value:
      # Generate aufs stuff
      self.generate_aufs_stacking(working_file.name)
    elif self.project.firmware[Key.LAYOUT.value][Key.METHOD.value] == Key.OVERLAYFS.value:
      # Generate overlayfs stuff
      self.generate_overlayfs_stacking(working_file.name)
    else:
      # If we reach this code, then method was unknown
      self.project.logging.critical("Unknown stacking method " +
                                    self.project.firmware[Key.LAYOUT.value][Key.METHOD.value])
      exit(1)

    # Update stack script permissions. It has to be executable and world readable (not reuiered
    # but easier to handle)
    os.chmod(working_file.name, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | \
             stat.S_IROTH | stat.S_IXOTH)

    # Generate the file path
    filepath = self.project.get_rootfs_mountpoint()
    filepath += '/usr/share/initramfs-tools/scripts/init-bottom/dft_create_stack'

    # And now we can move the temporary file under the rootfs tree
    command = "mv -f " + working_file.name + " " + filepath

    self.execute_command(command)

    # Final log
    logging.info("Firmware stacking has been successfully generated into : " + filepath)



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

    working_file.write("\n")
    working_file.write("\n")
    working_file.write("# ---------------------------------------------------------\n")
    working_file.write("# Generate Common mount commands\n")
    working_file.write("# ----------------------------------------------------------\n")
    working_file.write("\n")

    # Check that the stack definition is in the configuration file
    if Key.STACK_DEFINITION.value not in self.project.firmware[Key.LAYOUT.value]:
      self.project.logging.critical("The stack definition is not in the configuration file")
      exit(1)

    # Flag first item since mount point is different
#Todo ajouter un test sur le chemiin de montage qui doit etre absolu et virer le slash dans
#la generation

    # Create basic DFT directories structure
    working_file.write("# ----- Create basic DFT directories structure -----\n")
    working_file.write("mkdir -p " + self.dft_root + "/workdir\n")
    working_file.write("mkdir -p " + self.dft_root + "/mountpoint\n")
    working_file.write("\n")

    # Removing existing mounted root in order to use DFT root
    working_file.write("# ----- Umount initial root and remount our own -----\n")
    if self.stack_root != "/root":
      working_file.write("umount /root\n")
    working_file.write("umount " + self.stack_root + "\n")
    working_file.write("mkdir -p " + self.stack_root + "\n")

    # Mount the partition containing all the squashfs files
    working_file.write("mount -t " + self.project.firmware[Key.LAYOUT.value][Key.FILESYSTEM.value])
#    working_file.write(" " + self.project.firmware[Key.LAYOUT.value][Key.PARTITION.value])
    working_file.write(" ${ROOT} " + self.dft_root + "\n")

    # Iterates the stack items
    item_count = 0
    for item in self.project.firmware[Key.LAYOUT.value][Key.STACK_DEFINITION.value]:
      # Generate the mount point creation code
      working_file.write("\n")
      working_file.write("# ----- Mounting " + item[Key.STACK_ITEM.value]\
                         [Key.TYPE.value] + " '" + item[Key.STACK_ITEM.value][Key.NAME.value] +
                         "' -----\n")

      # Create the base working directory
      working_file.write("mkdir -p " + self.dft_root + "/")
      working_file.write(item[Key.STACK_ITEM.value][Key.NAME.value] + "\n")

      # ----- Generate the mount command to be used for a tmpfs ------------------------------------
      if item[Key.STACK_ITEM.value][Key.TYPE.value] == Key.TMPFS.value:
        working_file.write("mount -t tmpfs ")

        # Is there some defined options ?
        if Key.MOUNT_OPTIONS.value in item[Key.STACK_ITEM.value]:
          # Yes, then append the options to the command
          working_file.write("-o " + item[Key.STACK_ITEM.value][Key.MOUNT_OPTIONS.value] + " ")

        # Complete the mount command
        working_file.write("tmpfs " + self.dft_root +"/")
        working_file.write(item[Key.STACK_ITEM.value][Key.NAME.value] + "\n")
        working_file.write("mkdir -p " + self.dft_root + "/")
        working_file.write(item[Key.STACK_ITEM.value][Key.NAME.value] + "/mountpoint\n")

        # Create the workdir if we are using overlayfs (not needed for aufs)
        if self.project.firmware[Key.LAYOUT.value][Key.METHOD.value] == Key.OVERLAYFS.value:
          working_file.write("mkdir -p " + self.dft_root + "/")
          working_file.write(item[Key.STACK_ITEM.value][Key.NAME.value] + "/workdir\n")

      # ----- Generate the mount command to be used for a SQUASHFS file ----------------------------
      if item[Key.STACK_ITEM.value][Key.TYPE.value] == Key.SQUASHFS.value:
        working_file.write("DEV=$(losetup -f)\n")
        working_file.write("losetup ${DEV} " + self.dft_root + "/")
        working_file.write(self.project.firmware[Key.LAYOUT.value][Key.PATH.value] + "/")
        working_file.write(item[Key.STACK_ITEM.value][Key.SQUASHFS_FILE.value] + "\n")
        working_file.write("mount -t squashfs -o loop")

        # Is there some defined options ?
        if "mount-options" in item[Key.STACK_ITEM.value]:
          # Yes, then append the options to the command
          working_file.write("," + item[Key.STACK_ITEM.value][Key.MOUNT_OPTIONS.value])

        # Otherwise mount it to its dedicated moint
        working_file.write(" ${DEV} " + self.stack_root + "\n")

      # ----- Generate the mount command to be used for a partition --------------------------------
      if item[Key.STACK_ITEM.value][Key.TYPE.value] == Key.PARTITION.value:
        working_file.write("mount -t ext4 ")
#TODO: handle partition type from configuration file
        # Is there some defined options ?
        if "mount-options" in item[Key.STACK_ITEM.value]:
          # Yes, then append the options to the command
          working_file.write("-o " + item[Key.STACK_ITEM.value]["mount-options"] + " ")

        # Complete the mount command
#        working_file.write(item[Key.STACK_ITEM.value][Key.PARTITION.value] + " " + self.dft_root +
        working_file.write(" ${ROOT} " + self.dft_root +
                           "/" + item[Key.STACK_ITEM.value][Key.NAME.value] + "\n")


        # WIPPPPPPP
        working_file.write("mkdir -p " + self.dft_root + "/")
        working_file.write(item[Key.STACK_ITEM.value][Key.NAME.value] + "/mountpoint\n")

        # Create the workdir if we are using overlayfs (not needed for aufs)
        if self.project.firmware[Key.LAYOUT.value][Key.METHOD.value] == Key.OVERLAYFS.value:
          working_file.write("mkdir -p " + self.dft_root + "/")
          working_file.write(item[Key.STACK_ITEM.value][Key.NAME.value] + "/workdir\n")

      # Increments item counter
      item_count += 1

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
    working_file.write("\n")
    working_file.write("\n")
    working_file.write("# ---------------------------------------------------------\n")
    working_file.write("# Generate OverlayFS Stacking\n")
    working_file.write("# ----------------------------------------------------------\n")
    working_file.write("\n")

    self.project.logging.debug("Entering generate_overlayfs_stacking")

    # Check that the stack definition is in the configuration file
    if Key.STACK_DEFINITION.value not in self.project.firmware[Key.LAYOUT.value]:
      self.project.logging.critical("The stack definition is not in the configuration file")
      exit(1)

    # Iterates the stack items
    item_count = 0
    for item in self.project.firmware[Key.LAYOUT.value][Key.STACK_DEFINITION.value]:
      # Stack only if item is not the first
      if item_count == 0:
        # Increase the counter
        item_count += 1

        # Move to next item, which is the real first one to stck
        continue

      # Not there is already a mounted item, let's stack ! Generate the mount point creation code
      working_file.write("# Stack the " + item[Key.STACK_ITEM.value][Key.TYPE.value] +
                         " '" + item[Key.STACK_ITEM.value][Key.NAME.value] + "'\n")

      self.project.logging.debug("Generating overlay stacking for " + \
                                 item[Key.STACK_ITEM.value][Key.TYPE.value] + " " + \
                                 item[Key.STACK_ITEM.value][Key.NAME.value])

      # ----- Generate the tmpfs specific mount command --------------------------------------------
      if item[Key.STACK_ITEM.value][Key.TYPE.value] == Key.TMPFS.value:
        working_file.write("mount -t overlay -o lowerdir=" + self.stack_root)
        working_file.write(item[Key.STACK_ITEM.value][Key.MOUNTPOINT.value])
        working_file.write(",upperdir=" + self.dft_root + "/")
        working_file.write(item[Key.STACK_ITEM.value][Key.NAME.value] + "/mountpoint")
        working_file.write(",workdir="  + self.dft_root + "/")
        working_file.write(item[Key.STACK_ITEM.value][Key.NAME.value] + "/workdir")
        working_file.write(" overlay "  + self.stack_root)
        working_file.write(item[Key.STACK_ITEM.value][Key.MOUNTPOINT.value] + "\n")

      # ----- Generate the tmpfs specific mount command --------------------------------------------
      if item[Key.STACK_ITEM.value][Key.TYPE.value] == Key.SQUASHFS.value:
        working_file.write("mount -t overlay -o lowerdir=" + self.stack_root)
        working_file.write(item[Key.STACK_ITEM.value][Key.NAME.value] + ":")
        working_file.write(item[Key.STACK_ITEM.value][Key.MOUNTPOINT.value])
        working_file.write(" overlay "  + self.stack_root)
        working_file.write(item[Key.STACK_ITEM.value][Key.MOUNTPOINT.value] + "\n")

      # ----- Generate the tmpfs specific mount command --------------------------------------------
      if item[Key.STACK_ITEM.value][Key.TYPE.value] == Key.PARTITION.value:
        working_file.write("mount -t overlay -o lowerdir=" + self.stack_root)
        working_file.write(item[Key.STACK_ITEM.value][Key.MOUNTPOINT.value])
        working_file.write(",upperdir=" + self.dft_root + "/")
        working_file.write(item[Key.STACK_ITEM.value][Key.NAME.value] + "/mountpoint")
        working_file.write(",workdir=" + self.dft_root + "/")
        working_file.write(item[Key.STACK_ITEM.value][Key.NAME.value] + "/workdir")
        working_file.write(" overlay "  + self.stack_root)
        working_file.write(item[Key.STACK_ITEM.value][Key.MOUNTPOINT.value] + "\n")

      working_file.write("\n")

      # Increase item counter
      item_count += 1

    # We are done here, now close the file
    working_file.close()

    self.project.logging.debug("Exiting generate_overlayfs_stacking")


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

    # Reopen the working file
    working_file = open(working_file_name, "a")

    working_file.write("\n")
    working_file.write("\n")
    working_file.write("# ---------------------------------------------------------\n")
    working_file.write("# Generate AUFS Stacking\n")
    working_file.write("# ----------------------------------------------------------\n")
    working_file.write("\n")

#  mount -t aufs -o noatime,nodiratime,br:${systemdir}=rr -o udba=reval none ${mountdir}

    # We are done here, now close the file
    working_file.close()

    self.project.logging.debug("Exiting generate_aufs_stacking")
