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

""" This module implements The base class and functionnalities used by all the
cli targets.
"""

import os
import subprocess
import shutil

#
#    Class CliCommand
#
class CliCommand(object):
  """This class implements the base class used for all command fro cli

     It provides method used in all the derivated command, such has
     sudo execution and error handling, qemu setup and tear down, etc
  """

  # pylint: disable=too-many-instance-attributes

  # -------------------------------------------------------------------------
  #
  # __init__
  #
  # -------------------------------------------------------------------------
  def __init__(self, dft, project):
    """Default constructor
    """

    # Object storing the tool configuration. This object holds all the
    # definition of global configuration variales, such as tool installation
    # path, archive use, log level, etc
    self.dft = dft

    # Object storing the project definition. Project holds all the
    # configuration and definition used by the different stage of
    # the toolchain, including rootfs definition
    self.project = project

    # Retrieve the architecture of the host
    self.host_arch = subprocess.check_output("dpkg --print-architecture",
                                             shell=True).decode('UTF-8').rstrip()

    # Boolean used to flag the use of QEMU static
    self.use_qemu_static = (self.host_arch != project.target_arch)

    # Boolean used to flag if the cache archive is available. This value
    # is set by the setup_configuration method. Default is False, to
    # ensure it will be rebuild
    self.cache_archive_is_available = False

    # Flags used to remove 'mount bind' states
    self.proc_is_mounted = False
    self.devpts_is_mounted = False
    self.devshm_is_mounted = False

    # Flag used to prevent multiple call to cleanup since cleanup is used
    # in exception processing
    self.cleanup_in_progress = False

  # -------------------------------------------------------------------------
  #
  # execute_command
  #
  # -------------------------------------------------------------------------
  def execute_command(self, command):
    """ This method run a command as a subprocess. Typical use case is
    running sudo commands.

    This method is a wrapper to subprocess.run , and will be moved soon
    in a helper object. It provides mutalisation of error handling
    """

    self.project.logging.debug("running : " + command)

    try:
      # Execute the subprocess, output en errors are piped
      completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 shell=True, check=True, universal_newlines=False)

      # Return the output of the process to the caller
      return completed.stdout

    except subprocess.CalledProcessError as exception:
      self.cleanup_installation_files()
      self.project.logging.critical("Error %d occured when executing %s",
                                    exception.returncode, exception.cmd)
      exit(1)


  # -------------------------------------------------------------------------
  #
  # setup_qemu
  #
  # -------------------------------------------------------------------------
  def setup_qemu(self):
    """This method remove the QEMU static binary which has been previously
    copied to the target
    """

    # We should not execute if the flag is not set. Should have already
    # been tested, but double check by security
    if self.use_qemu_static != True:
      return

    # Copy the QEMU binary to the target, using root privileges
    if   self.project.target_arch == "armhf":
      qemu_target_arch = "arm"
    elif self.project.target_arch == "armel":
      qemu_target_arch = "arm"
    else:
      qemu_target_arch = self.project.target_arch

    self.project.logging.info("setting up QEMU for arch " +
                              self.project.target_arch +
                              " (using /usr/bin/qemu-" +
                              qemu_target_arch + "-static)")
    sudo_command = "sudo cp /usr/bin/qemu-"  + qemu_target_arch + "-static "
    sudo_command += self.project.rootfs_mountpoint + "/usr/bin/"
    self.execute_command(sudo_command)


  # -------------------------------------------------------------------------
  #
  # cleanup_qemu
  #
  # -------------------------------------------------------------------------
  def cleanup_qemu(self):
    """This method copy the QEMU static binary to the target
    """

    # We should not execute if the flag is not set. Should have already
    # been tested, but double check by security
    if self.use_qemu_static != True:
      return

    if self.project.dft.keep_bootstrap_files:
      self.project.logging.debug("keep_bootstrap_files is activated, keeping QEMU in " +
                                 self.project.rootfs_mountpoint)
      return

    # Copy the QEMU binary to the target, using root privileges
    if   self.project.target_arch == "armhf":
      qemu_target_arch = "arm"
    elif self.project.target_arch == "armel":
      qemu_target_arch = "arm"
    else:
      qemu_target_arch = self.project.target_arch

    # Execute the file removal with root privileges
    self.project.logging.info("cleaning QEMU for arch " + self.project.target_arch +
                              "(/usr/bin/qemu-" + qemu_target_arch + "-static)")
    os.system("sudo rm " + self.project.rootfs_mountpoint + "/usr/bin/qemu-" +
              qemu_target_arch + "-static")

  # -------------------------------------------------------------------------
  #
  # cleanup_installation_files
  #
  # -------------------------------------------------------------------------
  def cleanup_installation_files(self):
    """This method is in charge of cleaning processes after Ansible has
    been launched. In some case some daemons are still running inside the
    chroot, and they have to be stopped manually, or even killed in order
    to be able to umount /dev/ and /proc from inside the chroot
    """
    self.project.logging.info("starting to cleanup installation files")

    # Are we already doing a cleanup ? this may happens if an exception
    # occurs when cleaning up. It prevents multiple call and loop in
    # exception processing
    if self.cleanup_in_progress:
      return

    # Set the flag used to prevent multiple call
    self.cleanup_in_progress = True

    # Check if /proc is mounted, then umount it
    if self.proc_is_mounted:
      sudo_command = "sudo umount " + self.project.rootfs_mountpoint + "/dev/pts"
      self.execute_command(sudo_command)

    # Check if /dev/shm is mounted, then umount it
    if self.devshm_is_mounted:
      sudo_command = "sudo umount " + self.project.rootfs_mountpoint + "/dev/shm"
      self.execute_command(sudo_command)

    # Check if /dev/pts is mounted, then umount it
    if self.devpts_is_mounted:
      sudo_command = "sudo umount " + self.project.rootfs_mountpoint + "/proc"
      self.execute_command(sudo_command)

    self.cleanup_in_progress = False

    # Delete the DFT files from the rootfs
    if not self.project.dft.keep_bootstrap_files:
      if os.path.isdir(self.project.rootfs_mountpoint + "/dft_bootstrap"):
        shutil.rmtree(self.project.rootfs_mountpoint + "/dft_bootstrap")
    else:
      self.project.logging.debug("keep_bootstrap_files is activated, keeping DFT bootstrap " +
                                 "files in " + self.project.rootfs_mountpoint + "/dft_bootstrap")

    # Test if the generate_validity_check is defined, if not set the default value
    if "remove_validity_check" not in self.project.project_def["configuration"]:
      self.project.project_def["configuration"]["remove_validity_check"] = False

    if self.project.project_def["configuration"]["remove_validity_check"]:
      self.project.logging.debug("remove generated /etc/apt/apt.conf.d/10no-check-valid-until")

      # Generate the file path
      filepath = self.project.rootfs_mountpoint + "/etc/apt/apt.conf.d/10no-check-valid-until"

      # Test if the file exists
      if os.path.isfile(filepath):
        # Generate a rm command with root privileges and execute it
        sudo_command = "sudo rm -f " + filepath
        self.execute_command(sudo_command)
    else:
      msg = "remove_validity_check_ is set to False. Generated "
      msg += "/etc/apt/apt.conf.d/10no-check-valid-until is not removed"
      self.project.logging.debug(msg)



  # -------------------------------------------------------------------------
  #
  # remove_package
  #
  # -------------------------------------------------------------------------
  def remove_package(self, target):
    """This method deinstall a package or a list of packages from the target
    rootfs, and purge its configuration file. It will remove anything
    necessary to prevent having packages in the 'rc' state.

    This command is executed inside the chrooted environment and may need to
    have qemu installed.
    """

    self.project.logging.debug("Remove package : " + target)
    sudo_command = "sudo chroot " + self.project.rootfs_mountpoint
    sudo_command += " /usr/bin/apt-get autoremove --purge --yes " + target
    self.execute_command(sudo_command)


  # -------------------------------------------------------------------------
  #
  # install_package
  #
  # -------------------------------------------------------------------------
  def install_package(self, target):
    """This method install a package or a list of packages into the target
    rootfs.

    This command is executed inside the chrooted environment and may need to
    have qemu installed.
    """

    self.project.logging.debug("Install package(s) : " + target)
    sudo_command = "sudo chroot " + self.project.rootfs_mountpoint
    sudo_command += " /usr/bin/apt-get install --no-install-recommends --yes "
    sudo_command += " --allow-unauthenticated  " + target
    self.execute_command(sudo_command)

  # -------------------------------------------------------------------------
  #
  # update_package_catalog
  #
  # -------------------------------------------------------------------------
  def update_package_catalog(self):
    """This method updates the local catalog using the remote server defined
    in /etc/apt/sources.list.

    This command is executed inside the chrooted environment and may need to
    have qemu installed.
    """

    self.project.logging.debug("Updating APT catalog")
    sudo_command = "sudo chroot " + self.project.rootfs_mountpoint
    sudo_command += " /usr/bin/apt-get update --yes --allow-unauthenticated "
    self.execute_command(sudo_command)
