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
import errno
from enum import Enum
from dft.model import Key
from dft.ansi_colors import Colors


#-----------------------------------------------------------------------------
#
# class Output
#
# -----------------------------------------------------------------------------
class Output(Enum):
  """This class defines the destination when outputing strings. It can be
  either a log level or stdout.
  """

  # Define each and every key and associated string used in the tool
  DEBUG = "debug"
  INFO = "info"
  WARNING = "warning"
  ERROR = "error"
  CRITICAL = "critical"
  STDOUT = "stdout"



#-----------------------------------------------------------------------------
#
# class Code
#
# -----------------------------------------------------------------------------
class Code(Enum):
  """This class defines the different vales for result code when outputing a
  string ended by a result code.
  """

  # Define each and every key and associated string used in the tool
  SUCCESS = " OK "
  FAILURE = " KO "
  WARNING = "Warn"



# -----------------------------------------------------------------------------
#
#    Class CliCommand
#
# -----------------------------------------------------------------------------
class CliCommand(object):
  """This class implements the base class used for all command fro cli

     It provides method used in all the derivated command, such has
     command execution and error handling, qemu setup and tear down, etc
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
    self.host_arch = subprocess.check_output("uname -m", shell=True).decode(Key.UTF8.value).rstrip()

    # Subsititude arch synonyms to have coherence between tools output
    if self.host_arch == "x86_64":
      self.host_arch = "amd64"

    if self.host_arch == "armv7l":
      self.host_arch = "armhf"

    if self.host_arch == "aarch64":
      self.host_arch = "arm64"

    # Retrieve the architecture used by dpkg. This may be different in case of 32 bits systems
    # running with a 64 bits kernel. Example : kernel is ppc64, host userland is powerpc
    self.dpkg_arch = subprocess.check_output("dpkg --print-architecture",
                                             shell=True).decode(Key.UTF8.value).rstrip()

    # Boolean used to flag the use of QEMU static
    self.use_qemu_static = (self.host_arch != project.get_target_arch())
    self.use_debootstrap_arch = (self.dpkg_arch != project.get_target_arch())
    self.qemu_binary = None

    self.project.logging.debug("host_arch " + self.host_arch)
    self.project.logging.debug("target_arch " + project.get_target_arch())
    self.project.logging.debug("dpkg_arch " + self.dpkg_arch)

    # Flags used to remove 'mount bind' states
    self.proc_is_mounted = False
    self.devpts_is_mounted = False
    self.devshm_is_mounted = False

    # Flag used to prevent multiple call to cleanup since cleanup is used
    # in exception processing
    self.cleanup_in_progress = False

    # Defines the nuùber of column used to align text when outputing with right align
    # and the real size in char (without ansi escape codes) or the code
    self.right_align = 80
    self.len_str_code = 6



  # -------------------------------------------------------------------------
  #
  # execute_command
  #
  # -------------------------------------------------------------------------
  def execute_command(self, command):
    """ This method run a command as a subprocess. Typical use case is
    running commands.

    This method is a wrapper to subprocess.run , and will be moved soon
    in a helper object. It provides mutalisation of error handling
    """

    self.project.logging.debug("running : " + command)

    try:
      # Execute the subprocess, output ans errors are piped
      completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 shell=True, check=True, universal_newlines=False)

      # Return the output of the process to the caller
      return completed.stdout

    except subprocess.CalledProcessError as exception:
      self.cleanup_installation_files()
      self.project.logging.critical("Error %d occured when executing %s",
                                    exception.returncode, exception.cmd)
      self.project.logging.debug("stdout was :")
      self.project.logging.debug(exception.stdout)
      self.project.logging.debug("stderr was :")
      self.project.logging.debug(exception.stderr)
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
    if   self.project.get_target_arch() == "armhf":
      qemu_target_arch = "arm"
    elif self.project.get_target_arch() == "armel":
      qemu_target_arch = "arm"
    elif self.project.get_target_arch() == "arm64":
      qemu_target_arch = "aarch64"
    else:
      qemu_target_arch = self.project.get_target_arch()

    # qemu (static) has not a consistent naming among distributions. Gentoo
    # will name it 'qemu-ARCH' whereas debian will name it 'qemu-ARCH-static".
    qemu_candidates = [
        "/usr/bin/qemu-" + qemu_target_arch,
        "/usr/bin/qemu-" + qemu_target_arch + "-static"
    ]
    for qemu in qemu_candidates:
      # We first check that the candidate file exists
      if os.path.exists(qemu):
        # Then, we run the file command to check whether the qemu program is
        # statically linked or not. If this is true, we use this program as
        # the qemu-static for the target architecture.
        output = subprocess.check_output(["file", "--brief", "-L", qemu])
        # The output of file will be something like:
        # <type>, <arch>, <version>, <link type>, <interpreter>,  [...]
        # and we are interested in the 4th parameter (link type).
        link_info = output.decode(Key.UTF8.value).split(", ")[3]
        if link_info == "statically linked":
          self.qemu_binary = qemu
          break # Found, stop iterating.

    # Check that a valid qemu binary was found in the previous step
    if not self.qemu_binary:
      self.project.logging.critical("Failed to find qemu (static) for %s",
                                    qemu_target_arch)
      exit(1)

    # Generate the qemu binary name

    self.project.logging.info("setting up QEMU for arch " + self.project.get_target_arch() +
                              " (using " + self.qemu_binary + ")")
    command = "cp " + self.qemu_binary + " "
    command += self.project.get_rootfs_mountpoint() + "/usr/bin/"
    self.execute_command(command)


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
                                 self.project.get_rootfs_mountpoint())
      return

    # Remove he QEmu binary if it exist
    self.project.logging.info("cleaning QEMU for arch " + self.project.get_target_arch() +
                              "(using " + self.qemu_binary +")")
    try:
      os.remove(self.project.get_rootfs_mountpoint() + self.qemu_binary)

    # Catch OSError in case of file removal error
    except OSError as err:
      # If file does not exit errno value will be ENOENT
      if err.errno != errno.ENOENT:
        # Thus if exception was caused by something else, throw it upward
        raise

    # Empty the binary name
    self.qemu_binary = None



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

    # Delete the DFT files from the rootfs
    if not self.project.dft.keep_bootstrap_files:
      if os.path.isdir(self.project.get_rootfs_mountpoint() + "/dft_bootstrap"):
        shutil.rmtree(self.project.get_rootfs_mountpoint() + "/dft_bootstrap")
    else:
      self.project.logging.debug("keep_bootstrap_files is activated, keeping DFT bootstrap " +
                                 "files in " + self.project.get_rootfs_mountpoint() +
                                 "/dft_bootstrap")

    # Test if the generate_validity_check is defined, if not set the default value
    if "remove_validity_check" not in self.project.project["configuration"]:
      self.project.project["configuration"]["remove_validity_check"] = False

    if self.project.project["configuration"]["remove_validity_check"]:
      self.project.logging.debug("remove generated /etc/apt/apt.conf.d/10no-check-valid-until")

      # Generate the file path
      filepath = self.project.get_rootfs_mountpoint() + "/etc/apt/apt.conf.d/10no-check-valid-until"

      # Test if the file exists
      if os.path.isfile(filepath):
        try:
          os.remove(filepath)

        # Catch OSError in case of file removal error
        except OSError as err:
          # If file does not exit errno value will be ENOENT
          if err.errno != errno.ENOENT:
            # Thus if exception was caused by something else, throw it upward
            raise

    else:
      msg = "remove_validity_check is set to False. Generated "
      msg += "/etc/apt/apt.conf.d/10no-check-valid-until is not removed"
      self.project.logging.debug(msg)

    # Finally umount all the chrooted environment
    self.teardown_chrooted_environment()



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
    command = "chroot " + self.project.get_rootfs_mountpoint()
    command += " /usr/bin/apt-get autoremove --purge --yes " + target
    self.execute_command(command)


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
    command = "chroot " + self.project.get_rootfs_mountpoint()
    command += " /usr/bin/apt-get install --no-install-recommends --yes "
    command += " --allow-unauthenticated  " + target
    self.execute_command(command)



  # -------------------------------------------------------------------------
  #
  # add_catalog_signing_key
  #
  # -------------------------------------------------------------------------
  def add_catalog_signing_key(self, key):
    """This method add a new signing key to the list of known keys.
    """

    # Import the public key in the APT tools
    command = "LANG=C chroot " + self.project.get_rootfs_mountpoint()
    command += " apt-key adv --recv-keys --keyserver pgp.mit.edu " + key
    self.execute_command(command)



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
    command = "chroot " + self.project.get_rootfs_mountpoint()
    command += " /usr/bin/apt-get update --yes --allow-unauthenticated "
    self.execute_command(command)



  # -------------------------------------------------------------------------
  #
  # setup_chrooted_environment
  #
  # -------------------------------------------------------------------------
  def setup_chrooted_environment(self):
    """This method mount in the chrooted environment all of the special
    filesystems needed to make application work properly once chrooted.
    """

    # Mount bind /proc into the rootfs mountpoint
    command = "mount --bind --make-rslave /proc " + self.project.get_rootfs_mountpoint()
    command += "/proc"
    self.execute_command(command)
    self.proc_is_mounted = True

    # Mount bind /dev/pts into the rootfs mountpoint
    command = "mount --bind --make-rslave /dev/pts "
    command += self.project.get_rootfs_mountpoint() + "/dev/pts"
    self.execute_command(command)
    self.devpts_is_mounted = True

    # Mount bind /dev/shm into the rootfs mountpoint
    command = "mount --bind --make-rslave /dev/shm "
    command += self.project.get_rootfs_mountpoint() + "/dev/shm"
    self.execute_command(command)
    self.devshm_is_mounted = True



  # -------------------------------------------------------------------------
  #
  # teardown_chrooted_environment
  #
  # -------------------------------------------------------------------------
  def teardown_chrooted_environment(self):
    """This method umount in the chrooted environment all of the special
    filesystems needed to make application work properly once chrooted.
    """

    # Are we already doing a cleanup ? this may happens if an exception
    # occurs when cleaning up. It prevents multiple call and loop in
    # exception processing
    if self.cleanup_in_progress:
      return

    # Set the flag used to prevent multiple call
    self.cleanup_in_progress = True

    # Check if /proc is mounted, then umount it
    if self.proc_is_mounted:
      command = "umount " + self.project.get_rootfs_mountpoint() + "/dev/pts"
      self.execute_command(command)
      self.proc_is_mounted = False

    # Check if /dev/shm is mounted, then umount it
    if self.devshm_is_mounted:
      command = "umount " + self.project.get_rootfs_mountpoint() + "/dev/shm"
      self.execute_command(command)
      self.devshm_is_mounted = False

    # Check if /dev/pts is mounted, then umount it
    if self.devpts_is_mounted:
      command = "umount " + self.project.get_rootfs_mountpoint() + "/proc"
      self.execute_command(command)
      self.devpts_is_mounted = False

    self.cleanup_in_progress = False



  # -------------------------------------------------------------------------
  #
  # output_string_with_result
  #
  # -------------------------------------------------------------------------
  def output_string_with_result(self, msg, code):
    """ This method output a string followed by a result code. Resultat code
    is an enumed value. Color depends on code value:
      . OK      => Green
      . Warning => Orange
      . KO      => Red

    Result codes are right aligned to a value defined in this class members
    at init.
    """

    # Let's build the output string with padding and ANSI code for colors.
    # First the string fragment with ANSI codes
    str_code = "["

    # Complete with color according to the code
    if code == Code.SUCCESS:
      str_code += Colors.FG_GREEN.value
    elif code == Code.FAILURE:
      str_code += Colors.FG_RED.value
    if code == Code.WARNING:
      str_code += Colors.FG_ORANGE.value

    # Add bold, value, then go back to normal output
    str_code += Colors.BOLD.value + code.value + Colors.RESET.value + "]"

    # if the string is wider than alignment valuem then result code will be
    # on a new line. An extra 8 chars are remove from
    output = msg

    # We cannot use len(str_code) since it includes ANSI codes which are not printable
    # Instead we use the code_size constant which is the number of actual char printed
    if len(output) >= (self.right_align - self.len_str_code):
      output += "\n"
      output += "".join(" " for i in range(self.right_align - self.len_str_code))
    else:
      output += "".join(" " for i in range(self.right_align - len(output) - self.len_str_code))

    # Last thing to do is to concatenate the string with code and colors
    output += str_code
    output = str_code + " " + msg

    # And print it !
    print(output)


  # -------------------------------------------------------------------------
  #
  # display_test_result
  #
  # -------------------------------------------------------------------------
  def display_test_result(self, msg, target=Output.STDOUT):
    """ This method output a string either to stdout or log according to
    arguments. String is prefixed by the Hint keyword and is targetting
    hint's to explain why a test has failed.
    """

    # First add some padding since code are left aligned
    output = "".join(" " for i in range(self.len_str_code + 1))

    # Complete with color according to the code
    if target == Output.STDOUT:
      output += Colors.FG_CYAN.value
      output += Colors.BOLD.value + "Hint: " + Colors.RESET.value

    # if the string is wider than alignment valuem then result code will be
    # on a new line. An extra 8 chars are remove from
    output += msg

    # And print it !
    if target == Output.STDOUT:
      print(output)
    else:
      self.project.logging.log(output.value, output)
